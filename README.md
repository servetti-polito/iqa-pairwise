# Image Quality Assessment - Pairwise Comparison Tool

A Python Flask web application for conducting subjective image quality assessment studies. This tool allows researchers to present image pairs to users and collect their preferences with real-time synchronization across multiple viewing sessions.

## Features

- **Dual-page synchronized viewing**: Left and Right image viewers with real-time synchronization
- **Server-Sent Events**: Real-time communication between server and clients
- **Keyboard navigation**: Arrow keys for intuitive navigation through image pairs
- **Full-screen display**: Images displayed full-screen while preserving aspect ratio
- **CSV-based configuration**: Easy setup with simple CSV file format
- **Comprehensive feedback logging**: All user interactions logged with timestamps
- **Session summary**: Complete review of all choices made during the session
- **Data export**: Feedback data automatically saved to CSV for analysis

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/servetti-polito/iqa-pairwise.git
   cd iqa-pairwise
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your images**:
   - Place image files in the `static/images/` directory
   - Update `images.csv` with your image pairs

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the application**:
   - Main page: http://localhost:8000/
   - Left viewer: http://localhost:8000/left
   - Right viewer: http://localhost:8000/right

## Project Structure

```
iqa-pairwise/
├── app.py                    # Main Flask application
├── images.csv               # CSV file with image pairs
├── requirements.txt         # Python dependencies
├── create_sample_images.py  # Script to generate test images
├── templates/
│   ├── index.html          # Main navigation page
│   └── viewer.html         # Image viewer interface
├── static/
│   └── images/             # Directory for image files
└── README.md               # This file
```

## Usage Instructions

### For Researchers

1. **Prepare your images**: Place all images in the `static/images/` directory
2. **Configure image pairs**: Edit `images.csv` to list your image pairs (one pair per row)
3. **Start the server**: Run `python app.py`
4. **Open viewers**: Launch both left and right viewers in separate windows/tabs
5. **Collect data**: Feedback is automatically saved to `images_feedback.csv`

### For Participants

1. **Navigation**: Use Left (←) or Right (→) arrow keys to make choices
2. **Visual feedback**: Small colored indicators show when keys are pressed
3. **Session completion**: A summary of all choices is displayed at the end

## CSV File Formats

### Input: images.csv
```csv
left_image1.jpg,right_image1.jpg
left_image2.jpg,right_image2.jpg
left_image3.jpg,right_image3.jpg
```

### Output: images_feedback.csv
```csv
event_type,timestamp,key_pressed,left_image,right_image,image_index
start,2025-01-15T10:30:00.123456,,,,
feedback,2025-01-15T10:30:15.789012,ArrowLeft,image1_left.jpg,image1_right.jpg,0
feedback,2025-01-15T10:30:25.456789,ArrowRight,image2_left.jpg,image2_right.jpg,1
end,2025-01-15T10:35:00.987654,,,,
```

## API Endpoints

- `GET /` - Main navigation page
- `GET /left` - Left image viewer
- `GET /right` - Right image viewer
- `GET /events` - Server-Sent Events stream for real-time updates
- `POST /keypress` - Handle keyboard input from clients
- `GET /reset` - Reset to first image pair

## Technical Features

- **Multi-threaded Flask server** for handling multiple concurrent clients
- **Thread-safe queue system** for real-time message passing
- **Automatic reconnection** for SSE connections
- **Graceful error handling** for missing images or network issues
- **Responsive design** that works on different screen sizes

## Development

### Adding New Features

The application is designed to be easily extensible:

- **Custom key bindings**: Modify the keyboard event handlers in `viewer.html`
- **Additional metadata**: Extend the CSV logging format in `ImageManager.log_feedback()`
- **UI customization**: Update the CSS styles in `viewer.html`
- **New endpoints**: Add routes in `app.py` for additional functionality

### Testing

Generate sample images for testing:
```bash
python create_sample_images.py
```

This creates colorful placeholder images for development and testing.

## Requirements

- Python 3.7+
- Flask 2.3.3
- Modern web browser with Server-Sent Events support

## License

MIT License - feel free to use this for research or educational purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{iqa_pairwise_tool,
  title={Image Quality Assessment - Pairwise Comparison Tool},
  author={Your Name},
  year={2025},
  url={https://github.com/servetti-polito/iqa-pairwise}
}
```

## Support

For questions or issues, please open an issue on GitHub or contact the maintainer.
