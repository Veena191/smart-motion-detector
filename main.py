#!/usr/bin/env python3
"""
Smart Motion Detector - Main Application
Fintech security zone monitoring system using OpenCV
Author: Security Systems Division
"""

import cv2
import numpy as np
import json
import os
import sys
from datetime import datetime
from collections import deque
from utils.helpers import (
    check_after_hours,
    trigger_alert,
    save_clip,
    log_event,
    draw_overlay_text,
    check_roi_intersection
)


class MotionDetector:
    """Main motion detection class for security monitoring"""
    
    def __init__(self, config_path='config.json'):
        """Initialize the motion detector with configuration"""
        self.load_config(config_path)
        self.setup_directories()
        self.initialize_capture()
        self.build_background_model()
        self.motion_buffer = deque(maxlen=10)  # Buffer for smoothing detection
        self.recording = False
        self.record_start_time = None
        self.record_frames = []
        
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            print(f"[INFO] Configuration loaded from {config_path}")
        except Exception as e:
            print(f"[ERROR] Failed to load config: {e}")
            sys.exit(1)
            
    def setup_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs('data/recordings', exist_ok=True)
        os.makedirs('data/logs', exist_ok=True)
        print("[INFO] Directory structure verified")
        
    def initialize_capture(self):
        """Initialize video capture from configured source"""
        self.cap = cv2.VideoCapture(self.config['video_source'])
        if not self.cap.isOpened():
            print(f"[ERROR] Cannot open video source: {self.config['video_source']}")
            sys.exit(1)
        
        # Get video properties
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        if self.fps == 0:
            self.fps = 30  # Default fallback
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"[INFO] Video capture initialized: {self.width}x{self.height} @ {self.fps}fps")
        
    def build_background_model(self):
        """Build background model from initial frames using median"""
        print(f"[INFO] Building background model from {self.config['bg_frames']} frames...")
        frames = []
        
        for i in range(self.config['bg_frames']):
            ret, frame = self.cap.read()
            if not ret:
                print("[ERROR] Failed to capture frames for background model")
                sys.exit(1)
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            frames.append(gray)
            
            # Show progress
            cv2.putText(frame, f"Calibrating... {i+1}/{self.config['bg_frames']}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Smart Motion Detector', frame)
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
        
        # Calculate median background
        self.background = np.median(frames, axis=0).astype(np.uint8)
        print("[INFO] Background model created")
        
    def detect_motion(self, frame):
        """Detect motion in the current frame"""
        # Convert to grayscale and blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Compute difference from background
        frame_delta = cv2.absdiff(self.background, gray)
        
        # Threshold the difference
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        
        # Dilate to fill gaps
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        
        return contours, thresh
    
    def process_frame(self, frame):
        """Process a single frame for motion detection and visualization"""
        motion_detected = False
        roi_motion = False
        motion_boxes = []
        
        # Get ROI coordinates
        roi_x, roi_y, roi_w, roi_h = self.config['roi']
        
        # Detect motion
        contours, thresh = self.detect_motion(frame)
        
        # Process each contour
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Check if contour meets minimum area requirement
            if area >= self.config['min_area']:
                motion_detected = True
                x, y, w, h = cv2.boundingRect(contour)
                motion_boxes.append((x, y, w, h))
                
                # Check if motion intersects with ROI
                if check_roi_intersection((x, y, w, h), (roi_x, roi_y, roi_w, roi_h)):
                    roi_motion = True
                    # Draw red bounding box for motion in ROI
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                else:
                    # Draw yellow bounding box for motion outside ROI
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 1)
        
        # Draw ROI rectangle (green if no motion, red if motion detected)
        roi_color = (0, 0, 255) if roi_motion else (0, 255, 0)
        cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), 
                     roi_color, 2)
        cv2.putText(frame, "ROI", (roi_x + 5, roi_y + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, roi_color, 2)
        
        # Add overlays
        self.add_overlays(frame, roi_motion)
        
        return frame, roi_motion, thresh
    
    def add_overlays(self, frame, motion_detected):
        """Add text overlays and status indicators"""
        # Timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, timestamp, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Motion status
        if motion_detected:
            status_text = "MOTION DETECTED!"
            status_color = (0, 0, 255)
            # Status indicator circle
            cv2.circle(frame, (self.width - 30, 30), 10, (0, 0, 255), -1)
        else:
            status_text = "No Motion"
            status_color = (0, 255, 0)
            # Status indicator circle
            cv2.circle(frame, (self.width - 30, 30), 10, (0, 255, 0), -1)
        
        cv2.putText(frame, status_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Fintech label and watermark
        cv2.putText(frame, "Fintech Secure Zone", (10, self.height - 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, "SECURECAM-ATM-01", (10, self.height - 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # After-hours indicator
        start_hour, end_hour = self.config['alert_after_hours']
        if check_after_hours(start_hour, end_hour):
            cv2.putText(frame, "AFTER-HOURS MODE", (self.width - 200, self.height - 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)
    
    def handle_motion_event(self, frame):
        """Handle motion detection event - logging, alerts, recording"""
        # Check if we're in after-hours mode
        start_hour, end_hour = self.config['alert_after_hours']
        if not check_after_hours(start_hour, end_hour):
            return
        
        # Log the event
        message = f"Motion detected in ROI at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        log_event(message, 'data/logs/motion_log.txt')
        print(f"[ALERT] Motion detected in ROI!")
        
        # Trigger alert (sound if configured)
        if self.config.get('play_sound', False):
            trigger_alert()
        
        # Start recording if configured and not already recording
        if self.config.get('save_videos', True) and not self.recording:
            self.recording = True
            self.record_start_time = datetime.now()
            self.record_frames = []
            print(f"[INFO] Started recording motion event...")
    
    def update_recording(self, frame):
        """Update recording if in progress"""
        if not self.recording:
            return
        
        self.record_frames.append(frame.copy())
        
        # Check if recording duration exceeded
        elapsed = (datetime.now() - self.record_start_time).total_seconds()
        if elapsed >= self.config['record_duration']:
            # Save the recording
            timestamp = self.record_start_time.strftime("%Y%m%d_%H%M%S")
            output_path = f"data/recordings/motion_{timestamp}.avi"
            
            # Save using helper function
            save_clip(self.record_frames, output_path, 
                     self.config.get('output_fps', 20))
            
            print(f"[INFO] Recording saved: {output_path}")
            self.recording = False
            self.record_frames = []
    
    def run(self):
        """Main loop for motion detection"""
        print("[INFO] Motion detection started. Press 'q' to quit, 'r' to reset background")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("[WARNING] Failed to grab frame")
                break
            
            # Process frame
            processed_frame, roi_motion, thresh = self.process_frame(frame)
            
            # Handle motion events
            if roi_motion:
                self.motion_buffer.append(True)
                if sum(self.motion_buffer) >= 3:  # Require 3 frames of motion
                    self.handle_motion_event(processed_frame)
            else:
                self.motion_buffer.append(False)
            
            # Update recording if active
            self.update_recording(processed_frame)
            
            # Display recording indicator
            if self.recording:
                cv2.circle(processed_frame, (30, 30), 5, (0, 0, 255), -1)
                cv2.putText(processed_frame, "REC", (40, 35), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Show frames
            cv2.imshow('Smart Motion Detector', processed_frame)
            cv2.imshow('Motion Threshold', thresh)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                print("[INFO] Resetting background model...")
                self.build_background_model()
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("[INFO] Shutting down...")
        self.cap.release()
        cv2.destroyAllWindows()


def main():
    """Main entry point"""
    print("="*60)
    print("SMART MOTION DETECTOR - Fintech Security System")
    print("="*60)
    
    try:
        detector = MotionDetector('config.json')
        detector.run()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
