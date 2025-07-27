from flask import Flask, render_template, request, Response, jsonify
import csv
import json
import threading
import time
from queue import Queue
from datetime import datetime
import os

app = Flask(__name__)

class ImageManager:
    def __init__(self, csv_file='images.csv'):
        self.csv_file = csv_file
        self.image_pairs = []
        self.current_index = 0
        self.clients = []
        self.lock = threading.Lock()
        self.start_time = datetime.now()
        self.feedback_file = self._get_feedback_filename()
        self.feedback_data = []  # Store feedback for summary
        self._initialize_feedback_file()
        self.load_images()
    
    def _get_feedback_filename(self):
        """Generate feedback CSV filename based on images CSV filename"""
        base_name = os.path.splitext(self.csv_file)[0]
        return f"{base_name}_feedback.csv"
    
    def _initialize_feedback_file(self):
        """Initialize the feedback CSV file with headers and start time"""
        with open(self.feedback_file, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(['event_type', 'timestamp', 'key_pressed', 'left_image', 'right_image', 'image_index'])
            csv_writer.writerow(['start', self.start_time.isoformat(), '', '', '', ''])
        print(f"Initialized feedback file: {self.feedback_file}")
    
    def log_feedback(self, key_pressed, left_image, right_image):
        """Log user feedback to CSV file"""
        timestamp = datetime.now().isoformat()
        
        # Store feedback data for summary
        feedback_entry = {
            'timestamp': timestamp,
            'key_pressed': key_pressed,
            'left_image': left_image,
            'right_image': right_image,
            'image_index': self.current_index
        }
        self.feedback_data.append(feedback_entry)
        
        # Write to CSV file
        with open(self.feedback_file, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(['feedback', timestamp, key_pressed, left_image, right_image, self.current_index])
    
    def get_feedback_summary(self):
        """Generate a summary of all feedback given"""
        return self.feedback_data
    
    def log_end(self):
        """Log application end time"""
        end_time = datetime.now().isoformat()
        with open(self.feedback_file, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(['end', end_time, '', '', '', ''])
    
    def load_images(self):
        """Load image pairs from CSV file"""
        try:
            with open(self.csv_file, 'r') as file:
                csv_reader = csv.reader(file)
                self.image_pairs = list(csv_reader)
            print(f"Loaded {len(self.image_pairs)} image pairs from {self.csv_file}")
        except FileNotFoundError:
            print(f"CSV file {self.csv_file} not found. Creating sample data.")
            self.create_sample_csv()
            self.load_images()
    
    def create_sample_csv(self):
        """Create a sample CSV file for testing"""
        sample_data = [
            ['image1_left.jpg', 'image1_right.jpg'],
            ['image2_left.jpg', 'image2_right.jpg'],
            ['image3_left.jpg', 'image3_right.jpg'],
            ['image4_left.jpg', 'image4_right.jpg'],
            ['image5_left.jpg', 'image5_right.jpg']
        ]
        with open(self.csv_file, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(sample_data)
        print(f"Created sample CSV file: {self.csv_file}")
    
    def get_current_images(self):
        """Get current image pair"""
        if self.current_index < len(self.image_pairs):
            return self.image_pairs[self.current_index]
        return None, None
    
    def next_images(self):
        """Move to next image pair"""
        with self.lock:
            if self.current_index < len(self.image_pairs) - 1:
                self.current_index += 1
                return True
            return False
    
    def add_client(self, client_queue):
        """Add a new SSE client"""
        with self.lock:
            self.clients.append(client_queue)
    
    def remove_client(self, client_queue):
        """Remove an SSE client"""
        with self.lock:
            if client_queue in self.clients:
                self.clients.remove(client_queue)
    
    def broadcast_images(self, left_image, right_image):
        """Broadcast new images to all connected clients"""
        message = {
            'left_image': left_image,
            'right_image': right_image,
            'index': self.current_index
        }
        
        with self.lock:
            for client_queue in self.clients[:]:  # Create a copy to iterate safely
                try:
                    client_queue.put(message)
                except:
                    # Remove disconnected clients
                    self.clients.remove(client_queue)

# Global image manager instance
image_manager = ImageManager()

@app.route('/')
def index():
    """Main page with links to left and right pages"""
    return render_template('index.html')

@app.route('/left')
def left_page():
    """Left page showing left images"""
    return render_template('viewer.html', page_type='left')

@app.route('/right')
def right_page():
    """Right page showing right images"""
    return render_template('viewer.html', page_type='right')

@app.route('/events')
def events():
    """Server-Sent Events endpoint"""
    def event_stream():
        client_queue = Queue()
        image_manager.add_client(client_queue)
        
        try:
            # Send initial images
            left_image, right_image = image_manager.get_current_images()
            if left_image and right_image:
                yield f"data: {json.dumps({'left_image': left_image, 'right_image': right_image, 'index': image_manager.current_index})}\n\n"
            
            # Send updates as they come
            while True:
                try:
                    message = client_queue.get(timeout=30)  # 30 second timeout
                    yield f"data: {json.dumps(message)}\n\n"
                except:
                    break  # Timeout or error, close connection
        finally:
            image_manager.remove_client(client_queue)
    
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/keypress', methods=['POST'])
def handle_keypress():
    """Handle keyboard input from clients"""
    data = request.json
    key = data.get('key')
    left_image = data.get('left_image')
    right_image = data.get('right_image')
    
    print(f"Received keypress: {key}, Images: {left_image}, {right_image}")
    
    # Log the feedback
    image_manager.log_feedback(key, left_image, right_image)
    
    # Move to next images if left or right arrow key was pressed
    if key in ['ArrowLeft', 'ArrowRight']:
        if image_manager.next_images():
            new_left, new_right = image_manager.get_current_images()
            if new_left and new_right:
                image_manager.broadcast_images(new_left, new_right)
                return jsonify({'status': 'success', 'message': 'Images updated'})
            else:
                return jsonify({'status': 'error', 'message': 'No more images'})
        else:
            # Reached end of images - send summary
            summary = image_manager.get_feedback_summary()
            message = {
                'left_image': 'END',
                'right_image': 'END',
                'index': image_manager.current_index,
                'summary': summary
            }
            
            with image_manager.lock:
                for client_queue in image_manager.clients[:]:
                    try:
                        client_queue.put(message)
                    except:
                        image_manager.clients.remove(client_queue)
                        
            return jsonify({'status': 'end', 'message': 'Reached end of images', 'summary': summary})
    
    return jsonify({'status': 'ignored', 'message': f'Key {key} ignored'})

@app.route('/reset')
def reset():
    """Reset to first image pair"""
    image_manager.current_index = 0
    left_image, right_image = image_manager.get_current_images()
    if left_image and right_image:
        image_manager.broadcast_images(left_image, right_image)
    return jsonify({'status': 'reset', 'index': 0})

if __name__ == '__main__':
    print("Starting Image Comparison Server...")
    print("Access the application at:")
    print("  Main page: http://localhost:8000/")
    print("  Left page: http://localhost:8000/left")
    print("  Right page: http://localhost:8000/right")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        image_manager.log_end()
        print(f"Feedback data saved to: {image_manager.feedback_file}")
