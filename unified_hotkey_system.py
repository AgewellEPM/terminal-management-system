#!/usr/bin/env python3
"""
🎛️ UNIFIED HOTKEY SYSTEM
All terminal management hotkeys in one system
"""

import os
import sys
import time
import subprocess
import threading
import json
from pathlib import Path
from datetime import datetime
from queue import Queue

try:
    from pynput import keyboard, mouse
    import pyperclip
    from AppKit import NSPasteboard, NSPasteboardTypeFileURL, NSWorkspace
    import Cocoa
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip3 install pynput pyperclip pyobjc-framework-AppKit pyobjc-framework-Cocoa")
    sys.exit(1)

class UnifiedHotkeySystem:
    def __init__(self):
        self.pressed_keys = set()
        self.screenshot_queue = Queue()
        self.screenshot_path = None
        self.upload_mode = False
        self.mouse_listener = None
        
        # Define all hotkey combinations
        self.hotkeys = {
            'cmd_shift_9': {keyboard.Key.cmd, keyboard.Key.shift, keyboard.KeyCode.from_char('9')},
            'cmd_shift_8': {keyboard.Key.cmd, keyboard.Key.shift, keyboard.KeyCode.from_char('8')},
            'cmd_shift_0': {keyboard.Key.cmd, keyboard.Key.shift, keyboard.KeyCode.from_char('0')}
        }
        
        # Get project folder from terminal
        self.update_project_folder()
        
        print("🎛️ UNIFIED HOTKEY SYSTEM ACTIVE")
        print("=" * 40)
        print("⌨️ Hotkeys:")
        print("  📸 Cmd+Shift+0: Screenshot → Auto-upload")
        print("  🔥 Cmd+Shift+9: Terminal capture → File")
        print("  📝 Cmd+Shift+8: Terminal capture → TextEdit")
        print(f"  📁 Project: {self.project_folder}")
        print("\nPress ESC to exit")
        print()
        
    def update_project_folder(self):
        """Update current project folder based on active terminal"""
        try:
            # Check config file first
            config_path = Path.home() / ".claude" / "screenshot_config.json"
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    self.project_folder = config.get("current_folder", "General")
            else:
                self.project_folder = "General"
                
            # Update screenshot directory
            self.screenshot_dir = Path.home() / "Desktop" / "App_Images" / self.project_folder / "screenshots"
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
            
        except Exception as e:
            self.project_folder = "General"
            self.screenshot_dir = Path.home() / "Desktop" / "App_Images" / "General" / "screenshots"
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    def on_key_press(self, key):
        """Handle key press events"""
        self.pressed_keys.add(key)
        
        # Check for Cmd+Shift+0 (Smart Upload)
        if self.hotkeys['cmd_shift_0'].issubset(self.pressed_keys):
            self.handle_smart_upload()
            self.pressed_keys.clear()  # Prevent repeat
            
        # Check for Cmd+Shift+9 (Terminal to File)
        elif self.hotkeys['cmd_shift_9'].issubset(self.pressed_keys):
            self.handle_terminal_capture()
            self.pressed_keys.clear()
            
        # Check for Cmd+Shift+8 (Terminal to TextEdit)
        elif self.hotkeys['cmd_shift_8'].issubset(self.pressed_keys):
            self.handle_textedit_capture()
            self.pressed_keys.clear()
    
    def on_key_release(self, key):
        """Handle key release events"""
        self.pressed_keys.discard(key)
        
        # Exit on ESC
        if key == keyboard.Key.esc:
            print("\n👋 Exiting Unified System")
            if self.mouse_listener:
                self.mouse_listener.stop()
            return False
    
    def handle_smart_upload(self):
        """Handle Cmd+Shift+0 - Screenshot with auto-upload"""
        print("\n📸 Cmd+Shift+0: Taking screenshot for auto-upload...")
        
        # Update project folder
        self.update_project_folder()
        
        # Run in thread to not block
        thread = threading.Thread(target=self._smart_upload_process)
        thread.daemon = True
        thread.start()
    
    def _smart_upload_process(self):
        """Process smart upload in background"""
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"upload_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            
            # Take screenshot
            temp_path = Path("/tmp") / filename
            result = subprocess.run([
                'screencapture',
                '-i',  # Interactive mode
                '-x',  # No sound
                str(temp_path)
            ], capture_output=True)
            
            # Check if screenshot was taken
            if not temp_path.exists():
                print("❌ Screenshot cancelled")
                return
            
            # Move to project folder
            import shutil
            shutil.move(str(temp_path), str(filepath))
            self.screenshot_path = filepath
            
            print(f"✅ Saved: {self.project_folder}/{filename}")
            print("🎯 Click in any upload field to auto-upload")
            
            # Enable upload mode
            self.enable_upload_mode()
            
            # Show notification
            self.show_notification("Screenshot Ready", 
                                  f"Click to upload\n{self.project_folder}/{filename}")
            
        except Exception as e:
            print(f"❌ Screenshot error: {e}")
    
    def enable_upload_mode(self):
        """Enable click-to-upload mode"""
        self.upload_mode = True
        
        # Start mouse listener if needed
        if not self.mouse_listener or not self.mouse_listener.running:
            self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
            self.mouse_listener.start()
        
        # Auto-disable after 15 seconds
        timer = threading.Timer(15.0, self.disable_upload_mode)
        timer.daemon = True
        timer.start()
    
    def disable_upload_mode(self):
        """Disable upload mode"""
        if self.upload_mode:
            self.upload_mode = False
            print("⏰ Upload mode expired")
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse clicks for auto-upload"""
        if not pressed or not self.upload_mode or not self.screenshot_path:
            return
        
        if button != mouse.Button.left:
            return
        
        # Delay to let click register
        time.sleep(0.3)
        
        # Perform upload
        self.perform_upload()
        
        # Disable after upload
        self.upload_mode = False
    
    def perform_upload(self):
        """Upload the screenshot to clicked location"""
        try:
            print(f"📤 Uploading: {self.screenshot_path.name}")
            
            # Method 1: File pasteboard (for drag-drop capable apps)
            pasteboard = NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            
            file_url = Cocoa.NSURL.fileURLWithPath_(str(self.screenshot_path))
            pasteboard.writeObjects_([file_url])
            
            # Paste with Option for file
            subprocess.run([
                'osascript', '-e',
                'tell application "System Events" to keystroke "v" using {command down, option down}'
            ])
            
            time.sleep(0.3)
            
            # If that didn't work, try regular paste
            subprocess.run([
                'osascript', '-e',
                'tell application "System Events" to keystroke "v" using command down'
            ])
            
            print("✅ Upload complete!")
            self.show_notification("Uploaded", self.screenshot_path.name)
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
    
    def handle_terminal_capture(self):
        """Handle Cmd+Shift+9 - Terminal capture to file"""
        print("\n🔥 Cmd+Shift+9: Terminal capture to file")
        
        thread = threading.Thread(target=self._run_terminal_capture)
        thread.daemon = True
        thread.start()
    
    def _run_terminal_capture(self):
        """Run terminal capture in background"""
        try:
            subprocess.run([
                'python3', '/Users/lukekist/terminal_window_selector.py'
            ])
        except Exception as e:
            print(f"❌ Terminal capture error: {e}")
    
    def handle_textedit_capture(self):
        """Handle Cmd+Shift+8 - Terminal capture to TextEdit"""
        print("\n📝 Cmd+Shift+8: Terminal capture to TextEdit")
        
        thread = threading.Thread(target=self._run_textedit_capture)
        thread.daemon = True
        thread.start()
    
    def _run_textedit_capture(self):
        """Run TextEdit capture in background"""
        try:
            subprocess.run([
                'python3', '/Users/lukekist/terminal_capture_to_textedit.py'
            ])
        except Exception as e:
            print(f"❌ TextEdit capture error: {e}")
    
    def show_notification(self, title, message):
        """Show macOS notification"""
        try:
            script = f'display notification "{message}" with title "{title}" sound name "Glass"'
            subprocess.run(['osascript', '-e', script])
        except:
            pass
    
    def start(self):
        """Start the unified system"""
        with keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        ) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                print("\n👋 System stopped")

def main():
    """Main entry point"""
    try:
        system = UnifiedHotkeySystem()
        system.start()
    except KeyboardInterrupt:
        print("\n👋 Unified system stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()