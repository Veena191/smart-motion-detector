# Smart Motion Detector - Fintech Security System

A sophisticated motion detection system designed for fintech security applications, including ATM monitoring, vault surveillance, and after-hours intrusion detection. Built using classical computer vision techniques with OpenCV.

## 🎯 Features

- **ROI-Based Detection**: Define specific regions of interest for focused monitoring
- **After-Hours Mode**: Automatic activation during configured hours
- **Intelligent Background Modeling**: Median-based background subtraction for accurate motion detection
- **Video Recording**: Automatic recording of motion events with configurable duration
- **Event Logging**: Comprehensive logging of all motion detection events
- **Real-time Visualization**: Live display with motion indicators and status overlays
- **Configurable Sensitivity**: Adjustable thresholds for different environments

## 📋 Requirements

- Python 3.7 or higher
- Webcam or IP camera
- Windows/Linux/macOS

## 🚀 Quick Start

### Step 1: Create Project Structure

```bash
# Create main project directory
mkdir smart_motion_detector
cd smart_motion_detector

# Create subdirectories
mkdir -p utils data/recordings data/logs
```

### Step 2: Copy Project Files

Copy all provided files into their respective locations:
- `main.py` → root directory
- `config.json` → root directory
- `utils/__init__.py` → utils directory
- `utils/helpers.py` → utils directory
- `requirements.txt` → root directory
- `README.md` → root directory

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# If you encounter issues with pygame (audio), you can skip it:
pip install opencv-python numpy
# The system will fall back to system beep for alerts
```

### Step 4: Configure Settings

Edit `config.json` to customize the system:

```json
{
    "video_source": 0,              // 0 for default webcam, or video file path
    "bg_frames": 20,                // Frames for background model calibration
    "min_area": 5000,               // Minimum contour area for motion detection
    "roi": [150, 100, 300, 300],   // [x, y, width, height] of monitoring zone
    "alert_after_hours": [22, 6],   // Active hours [start_hour, end_hour]
    "record_duration": 5,            // Recording duration in seconds
    "save_videos": true,             // Enable/disable video recording
    "play_sound": false,             // Enable/disable audio alerts
    "output_fps": 20                 // FPS for saved video clips
}
```

### Step 5: Run the Application

```bash
python main.py
```

## 🎮 Controls

- **Q**: Quit the application
- **R**: Reset background model (useful if lighting changes)
- **ESC**: Exit any dialog windows

## 📸 Demo Instructions

### Setup Demo Environment

1. **Create a Mock ATM Zone**:
   - Print or write "ATM ZONE" on a paper
   - Place it in view of your webcam
   - Ensure good lighting for optimal detection

2. **Calibrate ROI**:
   - When the application starts, it will show the default ROI
   - Adjust the ROI in `config.json` to cover your ATM zone
   - Alternatively, modify the code to use `cv2.selectROI()` for interactive selection

3. **Test Motion Detection**:
   - Keep still during the initial calibration (20 frames)
   - Move your hand through the ROI area
   - Observe the red bounding box and "MOTION DETECTED!" status
   - Check `data/logs/motion_log.txt` for logged events
   - Find recorded clips in `data/recordings/`

### Testing Scenarios

#### Scenario 1: Normal Operations
- Set after-hours to current time range
- Trigger motion in ROI
- Verify recording and logging

#### Scenario 2: After-Hours Intrusion
- Set after-hours to exclude current time
- Trigger motion - no recording should occur
- Change config to include current time
- Trigger motion - recording should occur

#### Scenario 3: Sensitivity Testing
- Adjust `min_area` value
- Test with small movements (fingers) vs large movements (full body)
- Find optimal threshold for your environment

## 🏦 Fintech Use Cases

### ATM Monitoring
- Monitor customer areas for suspicious behavior
- Detect tampering attempts on ATM machines
- Record evidence of vandalism or theft attempts
- Reduce false alarms through ROI configuration

### Vault Security
- After-hours intrusion detection
- Motion-triggered recording to save storage
- Integration with existing security systems
- Automated alert generation for security personnel

### Branch Security
- Monitor restricted areas
- Track movement patterns in secure zones
- Generate activity reports for compliance
- Cost-effective alternative to continuous recording

## 🔧 Advanced Configuration

### Adjusting Sensitivity

The system's sensitivity can be tuned through several parameters:

1. **Background Frames** (`bg_frames`):
   - More frames = more stable background
   - Recommended: 20-30 for static environments

2. **Minimum Area** (`min_area`):
   - Higher value = ignore small movements
   - Lower value = detect subtle motion
   - Typical ranges: 1000-10000 pixels²

3. **Motion Threshold** (in code):
   - Located in `detect_motion()` method
   - Default: 25 (grayscale difference)
   - Increase for less sensitivity

### ROI Optimization

To determine optimal ROI coordinates:
1. Run the application
2. Take a screenshot when your target area is visible
3. Use an image editor to find pixel coordinates
4. Update `config.json` with new values

### Multi-Camera Setup

To use multiple cameras:
```python
# In config.json, set video_source to camera index:
"video_source": 1  // For second camera
"video_source": 2  // For third camera
```

## 📊 System Architecture

```
┌─────────────────┐
│   Video Input   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Background Model│
│   (Median of    │
│   N frames)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Frame Processing│
│ - Grayscale     │
│ - Gaussian Blur │
│ - Difference    │
│ - Threshold     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Contour Analysis│
│ - Area Filter   │
│ - ROI Check     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Motion Decision │
└────┬──────┬─────┘
     │      │
     ▼      ▼
┌────────┐ ┌──────────┐
│Logging │ │Recording │
└────────┘ └──────────┘
```

## 🐛 Troubleshooting

### Camera Not Found
```bash
# Check available cameras
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

### No Motion Detection
1. Check lighting conditions
2. Verify ROI placement
3. Lower `min_area` threshold
4. Reset background model (press 'R')

### High CPU Usage
- Reduce `output_fps` in config
- Increase frame processing interval
- Optimize ROI size

### Recording Issues
- Ensure `data/recordings/` directory exists
- Check disk space
- Verify codec support (try 'MJPG' instead of 'XVID')

## 🔒 Security Considerations

1. **Data Protection**: Recordings contain sensitive information - encrypt storage
2. **Access Control**: Restrict application access to authorized personnel
3. **Network Security**: If using IP cameras, ensure secure connections
4. **Compliance**: Ensure system meets local surveillance regulations
5. **Privacy**: Configure ROI to exclude private areas

## 📈 Performance Optimization

For production deployment:
1. Use hardware acceleration (GPU) when available
2. Implement motion detection zones
3. Add pre-recording buffer for context
4. Integrate with existing security infrastructure
5. Implement automatic cleanup of old recordings

## 📝 License

This project is designed for educational and commercial fintech security applications.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Machine learning-based person detection
- Multi-camera support
- Cloud storage integration
- Mobile app notifications
- Advanced analytics and reporting

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review configuration settings
3. Ensure all dependencies are installed
4. Verify hardware compatibility

## 🎉 Acknowledgments

Built with OpenCV and designed specifically for fintech security requirements.
