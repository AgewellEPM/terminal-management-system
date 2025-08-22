#!/usr/bin/env python3
"""
Smart Screenshot Upload System
Command+Shift+0: Take full page screenshot and enable auto-upload at cursor
"""

import os
import sys
import time
import subprocess
import threading
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

try:
    from pynput import keyboard, mouse
    from PIL import Image, ImageGrab
    import pyperclip
    from AppKit import NSPasteboard, NSPasteboardTypePNG, NSImage, NSData
    from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
    import Cocoa
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip3 install pynput pillow pyperclip pyobjc-framework-Quartz pyobjc-framework-Cocoa")
    sys.exit(1)

class SmartUploadSystem:
    def __init__(self):
        self.screenshot_path = None
        self.upload_mode = False
        self.mouse_listener = None
        self.last_screenshot_time = 0
        self.screenshot_dir = Path.home() / "Desktop" / "SmartUploads"
        self.screenshot_dir.mkdir(exist_ok=True)
        
        # Create temp directory for immediate uploads
        self.temp_dir = Path(tempfile.gettempdir()) / "smart_uploads"
        self.temp_dir.mkdir(exist_ok=True)
        
        print("🚀 Smart Upload System Started")
        print("📸 Cmd+Shift+0: Take full page screenshot")
        print("🎯 Click anywhere to auto-upload after screenshot")
        
    def take_full_screenshot(self):
        """Take a full screen screenshot and prepare for upload"""
        try:
            # Prevent rapid-fire screenshots
            current_time = time.time()
            if current_time - self.last_screenshot_time < 1:
                return
            self.last_screenshot_time = current_time
            
            print("\n📸 Taking full page screenshot...")
            
            # Generate timestamp filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"smart_upload_{timestamp}.png"
            
            # Save to both locations
            desktop_path = self.screenshot_dir / filename
            temp_path = self.temp_dir / "current_upload.png"
            
            # Take screenshot using screencapture
            subprocess.run([
                'screencapture',
                '-i',  # Interactive mode (allows selection)
                '-s',  # Capture selection
                '-x',  # No sound
                str(temp_path)
            ])
            
            # Check if screenshot was taken
            if not temp_path.exists():
                print("❌ Screenshot cancelled")
                return
                
            # Copy to desktop for permanent storage
            shutil.copy2(temp_path, desktop_path)
            
            # Load image to clipboard
            self.load_to_clipboard(temp_path)
            
            # Set current screenshot
            self.screenshot_path = temp_path
            
            # Enable upload mode
            self.enable_upload_mode()
            
            # Show notification
            self.show_notification("Screenshot Ready!", 
                                  f"Click anywhere to upload\n{filename}")
            
            print(f"✅ Screenshot saved: {filename}")
            print("🎯 Click in any upload field to paste automatically")
            
        except Exception as e:
            print(f"❌ Screenshot error: {e}")
            
    def load_to_clipboard(self, image_path):
        """Load image to system clipboard for pasting"""
        try:
            # Read image data
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Create NSData from image
            ns_data = NSData.dataWithBytes_length_(image_data, len(image_data))
            
            # Get system pasteboard
            pasteboard = NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            
            # Set image to pasteboard
            pasteboard.setData_forType_(ns_data, NSPasteboardTypePNG)
            
            print("📋 Image loaded to clipboard")
            
        except Exception as e:
            print(f"❌ Clipboard error: {e}")
            
    def enable_upload_mode(self):
        """Enable click-to-upload mode"""
        self.upload_mode = True
        
        # Start mouse listener if not running
        if not self.mouse_listener or not self.mouse_listener.running:
            self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
            self.mouse_listener.start()
            
        # Auto-disable after 30 seconds
        threading.Timer(30.0, self.disable_upload_mode).start()
        
    def disable_upload_mode(self):
        """Disable upload mode"""
        if self.upload_mode:
            self.upload_mode = False
            print("🔴 Upload mode disabled")
            
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse clicks for auto-upload"""
        if not pressed or not self.upload_mode:
            return
            
        try:
            # Small delay to let the click register
            time.sleep(0.1)
            
            # Check if we're in an upload-capable field
            if self.is_upload_field():
                self.perform_upload()
                
        except Exception as e:
            print(f"❌ Click handler error: {e}")
            
    def is_upload_field(self):
        """Check if current focus is an upload-capable field"""
        try:
            # Get active application
            workspace = Cocoa.NSWorkspace.sharedWorkspace()
            active_app = workspace.activeApplication()
            app_name = active_app.get('NSApplicationName', '')
            
            # Common apps that support image upload
            upload_apps = [
                'Safari', 'Google Chrome', 'Firefox', 'Slack', 
                'Discord', 'Messages', 'Mail', 'Notes', 'TextEdit',
                'Microsoft Teams', 'Zoom', 'Telegram', 'WhatsApp'
            ]
            
            if any(app in app_name for app in upload_apps):
                return True
                
            # Check for file input fields (web browsers)
            if app_name in ['Safari', 'Google Chrome', 'Firefox']:
                # Try to detect file input (this is a heuristic)
                return True
                
            return False
            
        except Exception as e:
            print(f"❌ Field detection error: {e}")
            return True  # Default to trying upload
            
    def perform_upload(self):
        """Perform the actual upload/paste operation"""
        try:
            print("📤 Uploading image...")
            
            # Try paste command (Cmd+V)
            subprocess.run([
                'osascript', '-e',
                'tell application "System Events" to keystroke "v" using command down'
            ])
            
            # Disable upload mode after successful upload
            self.disable_upload_mode()
            
            # Show success notification
            self.show_notification("Upload Complete!", 
                                  "Image pasted successfully")
            
            print("✅ Image uploaded!")
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
            
    def show_notification(self, title, message):
        """Show macOS notification"""
        try:
            subprocess.run([
                'osascript', '-e',
                f'display notification "{message}" with title "{title}" sound name "Glass"'
            ])
        except:
            pass
            
    def start(self):
        """Start the keyboard listener"""
        def on_press(key):
            try:
                # Check for Cmd+Shift+0
                if (hasattr(key, 'char') and key.char == '0' and 
                    self.is_cmd_shift_pressed()):
                    self.take_full_screenshot()
                    
            except Exception as e:
                pass
                
        def on_release(key):
            # Exit on ESC
            if key == keyboard.Key.esc:
                print("\n👋 Exiting Smart Upload System")
                return False
                
        # Store current pressed keys
        self.current_keys = set()
        
        def is_cmd_shift_pressed():
            """Check if Cmd+Shift is pressed"""
            return (keyboard.Key.cmd in self.current_keys and 
                   keyboard.Key.shift in self.current_keys)
                   
        self.is_cmd_shift_pressed = is_cmd_shift_pressed
        
        # Track key states
        def on_press_tracking(key):
            self.current_keys.add(key)
            return on_press(key)
            
        def on_release_tracking(key):
            self.current_keys.discard(key)
            return on_release(key)
            
        # Start keyboard listener
        with keyboard.Listener(
            on_press=on_press_tracking,
            on_release=on_release_tracking) as listener:
            listener.join()

def main():
    """Main entry point"""
    system = SmartUploadSystem()
    
    try:
        system.start()
    except KeyboardInterrupt:
        print("\n👋 Smart Upload System stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()