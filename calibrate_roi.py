#!/usr/bin/env python3
"""
ROI Calibration Tool for Smart Motion Detector
Helps users select and test ROI configuration
"""

import cv2
import json
import sys
import numpy as np


def load_config(config_path='config.json'):
    """Load current configuration"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return None


def save_config(config, config_path='config.json'):
    """Save configuration to file"""
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Configuration saved to {config_path}")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def select_roi_mode():
    """Interactive ROI selection mode"""
    print("\n" + "="*60)
    print("ROI SELECTION MODE")
    print("="*60)
    print("Instructions:")
    print("1. The camera feed will open")
    print("2. Click and drag to select the monitoring zone")
    print("3. Press SPACE/ENTER to confirm selection")
    print("4. Press 'c' to cancel and keep current ROI")
    print("5. Press 'q' to quit without saving")
    print("\nPress any key to continue...")
    
    # Load config
    config = load_config()
    if not config:
        return
    
    # Open camera
    cap = cv2.VideoCapture(config['video_source'])
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return
    
    # Get a frame for ROI selection
    ret, frame = cap.read()
    if not ret:
        print("Error: Cannot read from camera")
        cap.release()
        return
    
    # Draw current ROI on frame
    current_roi = config['roi']
    display_frame = frame.copy()
    cv2.rectangle(display_frame, 
                 (current_roi[0], current_roi[1]),
                 (current_roi[0] + current_roi[2], current_roi[1] + current_roi[3]),
                 (0, 255, 0), 2)
    cv2.putText(display_frame, "Current ROI", 
               (current_roi[0], current_roi[1] - 10),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Show current ROI
    cv2.imshow("Current ROI Configuration", display_frame)
    cv2.waitKey(2000)
    
    # Select new ROI
    print("\nSelect new ROI...")
    roi = cv2.selectROI("Select ROI (SPACE to confirm, ESC to cancel)", 
                        frame, fromCenter=False, showCrosshair=True)
    
    cv2.destroyAllWindows()
    cap.release()
    
    # Check if selection was made
    if roi[2] > 0 and roi[3] > 0:
        new_roi = [int(roi[0]), int(roi[1]), int(roi[2]), int(roi[3])]
        print(f"\nNew ROI selected: {new_roi}")
        
        # Ask for confirmation
        confirm = input("Save this ROI to config.json? (y/n): ").lower()
        if confirm == 'y':
            config['roi'] = new_roi
            if save_config(config):
                print("ROI updated successfully!")
            else:
                print("Failed to save ROI")
        else:
            print("ROI not saved")
    else:
        print("ROI selection cancelled")


def test_roi_mode():
    """Test current ROI configuration with live preview"""
    print("\n" + "="*60)
    print("ROI TESTING MODE")
    print("="*60)
    print("Testing current ROI configuration...")
    print("Move objects through the ROI to test detection")
    print("Press 'q' to quit\n")
    
    # Load config
    config = load_config()
    if not config:
        return
    
    # Open camera
    cap = cv2.VideoCapture(config['video_source'])
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return
    
    # Build simple background model
    print("Building background model (stay still)...")
    bg_frames = []
    for i in range(config['bg_frames']):
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            bg_frames.append(gray)
    
    background = np.median(bg_frames, axis=0).astype(np.uint8)
    print("Background model ready. Starting detection...\n")
    
    roi_x, roi_y, roi_w, roi_h = config['roi']
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Detect motion
        frame_delta = cv2.absdiff(background, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        
        motion_in_roi = False
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= config['min_area']:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check ROI intersection
                if (x < roi_x + roi_w and x + w > roi_x and
                    y < roi_y + roi_h and y + h > roi_y):
                    motion_in_roi = True
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        
        # Draw ROI
        roi_color = (0, 0, 255) if motion_in_roi else (0, 255, 0)
        cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), 
                     roi_color, 2)
        
        # Add status text
        status = "MOTION IN ROI!" if motion_in_roi else "No motion in ROI"
        color = (0, 0, 255) if motion_in_roi else (0, 255, 0)
        cv2.putText(frame, status, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        cv2.putText(frame, f"ROI: [{roi_x}, {roi_y}, {roi_w}, {roi_h}]", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, "Press 'q' to quit", 
                   (10, frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Show frames
        cv2.imshow('ROI Test - Main View', frame)
        cv2.imshow('ROI Test - Motion Threshold', thresh)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nROI testing completed")


def show_current_config():
    """Display current configuration"""
    print("\n" + "="*60)
    print("CURRENT CONFIGURATION")
    print("="*60)
    
    config = load_config()
    if config:
        for key, value in config.items():
            print(f"{key:20s}: {value}")
    else:
        print("Could not load configuration")


def main():
    """Main calibration menu"""
    while True:
        print("\n" + "="*60)
        print("SMART MOTION DETECTOR - ROI Calibration Tool")
        print("="*60)
        print("1. Show current configuration")
        print("2. Select new ROI")
        print("3. Test ROI with live preview")
        print("4. Exit")
        print()
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            show_current_config()
        elif choice == '2':
            select_roi_mode()
        elif choice == '3':
            test_roi_mode()
        elif choice == '4':
            print("Exiting calibration tool...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCalibration tool interrupted by user")
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"\nError: {e}")
        cv2.destroyAllWindows()
