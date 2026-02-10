#!/usr/bin/env python3
"""
Test script to verify Smart Motion Detector installation
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing module imports...")
    
    try:
        import cv2
        print(f"✓ OpenCV version: {cv2.__version__}")
    except ImportError:
        print("✗ OpenCV not installed. Run: pip install opencv-python")
        return False
    
    try:
        import numpy as np
        print(f"✓ NumPy version: {np.__version__}")
    except ImportError:
        print("✗ NumPy not installed. Run: pip install numpy")
        return False
    
    try:
        import pygame
        print(f"✓ pygame installed (optional) - version: {pygame.version.ver}")
    except ImportError:
        print("○ pygame not installed (optional, alerts will use system beep)")
    
    return True


def test_camera():
    """Test if camera is accessible"""
    print("\nTesting camera access...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print("✓ Camera is accessible")
                return True
            else:
                print("✗ Camera found but cannot read frames")
                return False
        else:
            print("✗ No camera detected on index 0")
            print("  Try changing 'video_source' in config.json")
            return False
    except Exception as e:
        print(f"✗ Error accessing camera: {e}")
        return False


def test_project_structure():
    """Test if project structure is correct"""
    print("\nChecking project structure...")
    
    required_files = [
        'main.py',
        'config.json',
        'requirements.txt',
        'README.md',
        'utils/__init__.py',
        'utils/helpers.py'
    ]
    
    required_dirs = [
        'data',
        'data/recordings',
        'data/logs',
        'utils'
    ]
    
    all_good = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ Missing: {file}")
            all_good = False
    
    for dir in required_dirs:
        if os.path.isdir(dir):
            print(f"✓ {dir}/")
        else:
            print(f"✗ Missing directory: {dir}/")
            all_good = False
    
    return all_good


def test_config():
    """Test if configuration file is valid"""
    print("\nValidating configuration...")
    
    try:
        import json
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        required_keys = ['video_source', 'bg_frames', 'min_area', 'roi', 
                        'alert_after_hours', 'record_duration']
        
        for key in required_keys:
            if key in config:
                print(f"✓ Config: {key} = {config[key]}")
            else:
                print(f"✗ Missing config key: {key}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Error reading config: {e}")
        return False


def main():
    print("="*60)
    print("SMART MOTION DETECTOR - Installation Test")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Project Structure", test_project_structure),
        ("Configuration", test_config),
        ("Camera Access", test_camera)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ Test '{name}' failed with error: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    if all(results):
        print("SUCCESS: All tests passed! ✓")
        print("You can now run: python main.py")
    else:
        print("FAILURE: Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
