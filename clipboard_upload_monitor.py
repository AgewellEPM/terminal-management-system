#!/usr/bin/env python3
"""
Clipboard Upload Monitor
Monitors clipboard for screenshots and enables auto-upload on click
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
from datetime import datetime

try:
    from pynput import mouse
    import pyperclip
    from AppKit import NSPasteboard, NSPasteboardTypePNG, NSPasteboardTypeString
    from PIL import ImageGrab
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip3 install pynput pyperclip pillow pyobjc-framework-AppKit")
    sys.exit(1)

class ClipboardUploadMonitor:
    def __init__(self):
        self.last_clipboard_check = None
        self.has_image = False
        self.upload_enabled = False
        self.mouse_listener = None
        self.monitoring = True
        
        # Create directory for saved screenshots
        self.screenshot_dir = Path.home() / "Desktop" / "SmartUploads"
        self.screenshot_dir.mkdir(exist_ok=True)
        
        print("📋 Clipboard Upload Monitor Started")
        print("=====================================")
        print("📸 Take any screenshot (Cmd+Shift+4)")
        print("🎯 Click in any upload field to auto-paste")
        print("⌨️ Works with Cmd+Shift+0 for instant capture")
        print()
        
    def check_clipboard(self):
        """Check if clipboard contains an image"""
        try:
            pasteboard = NSPasteboard.generalPasteboard()
            
            # Check for image data
            if pasteboard.dataForType_(NSPasteboardTypePNG):
                return True
                
            # Check for file URLs (screenshots)
            files = pasteboard.propertyListForType_("NSFilenamesPboardType")
            if files:
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        return True
                        
            return False
            
        except Exception as e:
            return False
            
    def monitor_clipboard(self):
        """Monitor clipboard for new screenshots"""
        print("👀 Monitoring clipboard for screenshots...")
        
        while self.monitoring:
            try:
                # Check if clipboard has image
                current_has_image = self.check_clipboard()
                
                # If new image detected
                if current_has_image and not self.has_image:
                    self.has_image = True
                    self.on_screenshot_detected()
                elif not current_has_image:
                    self.has_image = False
                    self.upload_enabled = False
                    
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(1)
                
    def on_screenshot_detected(self):
        """Handle screenshot detection"""
        print("\n🎯 Screenshot detected in clipboard!")
        print("   Click anywhere to upload/paste")
        
        # Enable upload mode
        self.upload_enabled = True
        
        # Start mouse listener if needed
        if not self.mouse_listener or not self.mouse_listener.running:
            self.mouse_listener = mouse.Listener(on_click=self.on_click)
            self.mouse_listener.start()
            
        # Show notification
        self.show_notification("Screenshot Ready", 
                              "Click in any field to auto-paste")
        
        # Auto-disable after 30 seconds
        threading.Timer(30.0, self.disable_upload).start()
        
    def disable_upload(self):
        """Disable upload mode"""
        if self.upload_enabled:
            self.upload_enabled = False
            print("⏰ Upload mode timed out")
            
    def on_click(self, x, y, button, pressed):
        """Handle mouse clicks"""
        if not pressed or not self.upload_enabled:
            return
            
        # Small delay for click to register
        time.sleep(0.2)
        
        # Perform paste
        self.paste_image()
        
        # Disable upload mode
        self.upload_enabled = False
        
    def paste_image(self):
        """Paste the image using Cmd+V"""
        try:
            print("📤 Pasting image...")
            
            # Use AppleScript to paste
            script = '''
            tell application "System Events"
                keystroke "v" using command down
            end tell
            '''
            
            subprocess.run(['osascript', '-e', script])
            
            print("✅ Image pasted!")
            
            # Show success notification
            self.show_notification("Upload Complete", 
                                  "Image pasted successfully")
            
        except Exception as e:
            print(f"❌ Paste error: {e}")
            
    def show_notification(self, title, message):
        """Show macOS notification"""
        try:
            script = f'display notification "{message}" with title "{title}" sound name "Glass"'
            subprocess.run(['osascript', '-e', script])
        except:
            pass
            
    def start(self):
        """Start monitoring"""
        try:
            # Start clipboard monitor in thread
            monitor_thread = threading.Thread(target=self.monitor_clipboard)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            print("Press Ctrl+C to stop\n")
            
            # Keep main thread alive
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n👋 Clipboard monitor stopped")
            self.monitoring = False
            sys.exit(0)

def main():
    """Main entry point"""
    monitor = ClipboardUploadMonitor()
    monitor.start()

if __name__ == "__main__":
    main()