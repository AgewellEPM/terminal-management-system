#!/usr/bin/env python3
"""
Auto Upload Anywhere System
Command+Shift+0: Take screenshot, route to folder, and auto-upload wherever cursor points
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
from datetime import datetime
import json

try:
    from pynput import keyboard, mouse
    from PIL import ImageGrab
    import pyperclip
    from AppKit import NSPasteboard, NSPasteboardTypeFileURL, NSWorkspace
    from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
    import Cocoa
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip3 install pynput pillow pyperclip pyobjc-framework-Quartz pyobjc-framework-Cocoa")
    sys.exit(1)

class AutoUploadAnywhere:
    def __init__(self):
        self.screenshot_path = None
        self.upload_ready = False
        self.mouse_listener = None
        
        # Get active terminal project folder
        self.project_folder = self.get_active_project_folder()
        
        # Screenshot directory based on active project
        self.screenshot_dir = Path.home() / "Desktop" / "App_Images" / self.project_folder / "screenshots"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        print("🚀 Auto Upload Anywhere System")
        print("=" * 40)
        print(f"📁 Screenshots → {self.project_folder}")
        print("📸 Cmd+Shift+0: Screenshot + Auto-upload")
        print("🎯 Point cursor at any upload field")
        print()
        
    def get_active_project_folder(self):
        """Get the active project based on terminal focus"""
        try:
            # Read the screenshot config to get active project
            config_path = Path.home() / ".claude" / "screenshot_config.json"
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    return config.get("current_folder", "General")
                    
            # Check for active terminal window title
            script = '''
            tell application "Terminal"
                if (count of windows) > 0 then
                    return name of front window
                end if
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            if result.stdout:
                # Extract project name from terminal title
                title = result.stdout.strip()
                if "🟢" in title:
                    # Remove emoji and clean up
                    project = title.replace("🟢", "").strip()
                    project = project.split("—")[0].strip()
                    return project if project else "General"
                    
        except Exception as e:
            print(f"Project detection error: {e}")
            
        return "General"
        
    def take_screenshot_and_prepare(self):
        """Take screenshot, save to project folder, and prepare for upload"""
        try:
            print(f"\n📸 Taking screenshot...")
            
            # Update project folder in case it changed
            self.project_folder = self.get_active_project_folder()
            self.screenshot_dir = Path.home() / "Desktop" / "App_Images" / self.project_folder / "screenshots"
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            
            # Take interactive screenshot
            temp_path = Path("/tmp") / filename
            result = subprocess.run([
                'screencapture',
                '-i',  # Interactive mode
                '-x',  # No sound
                str(temp_path)
            ])
            
            # Check if screenshot was taken
            if not temp_path.exists():
                print("❌ Screenshot cancelled")
                return False
                
            # Move to project folder
            import shutil
            shutil.move(str(temp_path), str(filepath))
            
            # Store path for upload
            self.screenshot_path = filepath
            
            print(f"✅ Saved to: {self.project_folder}/screenshots/{filename}")
            
            # Enable upload mode
            self.enable_upload_mode()
            
            return True
            
        except Exception as e:
            print(f"❌ Screenshot error: {e}")
            return False
            
    def enable_upload_mode(self):
        """Enable click-to-upload mode"""
        self.upload_ready = True
        
        print("🎯 Click in any upload field to auto-upload")
        print("   (Discord, Slack, Browser, etc.)")
        
        # Start mouse listener
        if not self.mouse_listener or not self.mouse_listener.running:
            self.mouse_listener = mouse.Listener(on_click=self.on_click)
            self.mouse_listener.start()
            
        # Auto-disable after 20 seconds
        threading.Timer(20.0, self.disable_upload_mode).start()
        
    def disable_upload_mode(self):
        """Disable upload mode"""
        if self.upload_ready:
            self.upload_ready = False
            print("⏰ Upload mode timed out")
            
    def on_click(self, x, y, button, pressed):
        """Handle mouse clicks for auto-upload"""
        if not pressed or not self.upload_ready or not self.screenshot_path:
            return
            
        # Only process left clicks
        if button != mouse.Button.left:
            return
            
        # Small delay to let click register
        time.sleep(0.3)
        
        # Check if we're in an uploadable context
        if self.is_upload_context():
            self.perform_upload()
            
    def is_upload_context(self):
        """Check if current app/field supports file upload"""
        try:
            # Get active application
            workspace = NSWorkspace.sharedWorkspace()
            active_app = workspace.activeApplication()
            app_name = active_app.get('NSApplicationName', '')
            
            # Apps that support drag-drop or file upload
            upload_apps = [
                'Safari', 'Google Chrome', 'Firefox', 'Arc',
                'Slack', 'Discord', 'Telegram', 'WhatsApp',
                'Messages', 'Mail', 'Notes', 'TextEdit',
                'Microsoft Teams', 'Zoom', 'Skype',
                'Finder', 'Preview', 'Photos',
                'Twitter', 'Facebook', 'Instagram'
            ]
            
            return any(app in app_name for app in upload_apps)
            
        except Exception:
            return True  # Default to trying
            
    def perform_upload(self):
        """Perform the upload by simulating drag-drop or file selection"""
        try:
            print(f"📤 Uploading: {self.screenshot_path.name}")
            
            # Method 1: Try drag-drop simulation
            if self.try_drag_drop():
                print("✅ Uploaded via drag-drop!")
                self.upload_ready = False
                return
                
            # Method 2: Try file dialog injection
            if self.try_file_dialog():
                print("✅ Uploaded via file dialog!")
                self.upload_ready = False
                return
                
            # Method 3: Copy file path and paste
            if self.try_paste_path():
                print("✅ Uploaded via paste!")
                self.upload_ready = False
                return
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
            
    def try_drag_drop(self):
        """Simulate drag and drop of file"""
        try:
            # Put file path in pasteboard as file URL
            pasteboard = NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            
            # Create file URL
            file_url = Cocoa.NSURL.fileURLWithPath_(str(self.screenshot_path))
            pasteboard.writeObjects_([file_url])
            
            # Simulate paste which may trigger file upload
            script = '''
            tell application "System Events"
                keystroke "v" using {command down, option down}
            end tell
            '''
            subprocess.run(['osascript', '-e', script])
            
            time.sleep(0.5)
            return True
            
        except Exception:
            return False
            
    def try_file_dialog(self):
        """Try to inject file into file dialog if open"""
        try:
            # Check if a file dialog is open
            script = '''
            tell application "System Events"
                if exists (window 1 of process 1 whose subrole is "AXStandardWindow") then
                    -- Type the file path
                    keystroke "g" using {command down, shift down}
                    delay 0.5
                    keystroke "%s"
                    delay 0.5
                    keystroke return
                    delay 0.5
                    keystroke return
                    return true
                end if
            end tell
            ''' % str(self.screenshot_path)
            
            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True)
            return "true" in result.stdout
            
        except Exception:
            return False
            
    def try_paste_path(self):
        """Copy file to clipboard and paste"""
        try:
            # Copy file path to clipboard
            pyperclip.copy(str(self.screenshot_path))
            
            # Try to paste
            script = '''
            tell application "System Events"
                keystroke "v" using command down
            end tell
            '''
            subprocess.run(['osascript', '-e', script])
            
            return True
            
        except Exception:
            return False
            
    def show_notification(self, title, message):
        """Show macOS notification"""
        try:
            script = f'display notification "{message}" with title "{title}" sound name "Glass"'
            subprocess.run(['osascript', '-e', script])
        except:
            pass

class HotkeyHandler:
    """Handle Command+Shift+0 hotkey"""
    
    def __init__(self, uploader):
        self.uploader = uploader
        self.current_keys = set()
        
    def start(self):
        """Start listening for hotkeys"""
        print("⌨️ Listening for Cmd+Shift+0...")
        
        def on_press(key):
            self.current_keys.add(key)
            
            # Check for Cmd+Shift+0
            if (keyboard.Key.cmd in self.current_keys and
                keyboard.Key.shift in self.current_keys):
                if hasattr(key, 'char') and key.char == '0':
                    print("\n🔥 Cmd+Shift+0 detected!")
                    # Run in thread to not block
                    threading.Thread(
                        target=self.uploader.take_screenshot_and_prepare
                    ).start()
                    
        def on_release(key):
            self.current_keys.discard(key)
            
            # Exit on ESC
            if key == keyboard.Key.esc:
                print("\n👋 Exiting...")
                return False
                
        with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
            listener.join()

def main():
    """Main entry point"""
    try:
        uploader = AutoUploadAnywhere()
        hotkey = HotkeyHandler(uploader)
        hotkey.start()
        
    except KeyboardInterrupt:
        print("\n👋 Auto Upload System stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()