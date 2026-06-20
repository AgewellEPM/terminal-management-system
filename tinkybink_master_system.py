#!/usr/bin/env python3
"""
🐷 TINKYBINK MASTER SYSTEM - Everything in ONE
Menu bar, hotkeys, screenshot routing, green dots - all unified
"""

import os
import sys
import time
import json
import shutil
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from queue import Queue

# Import all needed libraries
try:
    # Menu bar
    import rumps
    # Keyboard/Mouse
    from pynput import keyboard, mouse
    # Screenshot monitoring
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    # Clipboard and system
    import pyperclip
    from AppKit import NSPasteboard, NSWorkspace, NSURL
    import Cocoa
except ImportError as e:
    print(f"Installing dependencies: {e}")
    os.system("pip3 install rumps pynput watchdog pyperclip pyobjc-framework-AppKit pyobjc-framework-Cocoa")
    import rumps
    from pynput import keyboard, mouse
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    import pyperclip
    from AppKit import NSPasteboard, NSWorkspace, NSURL
    import Cocoa

class TinkyBinkMasterSystem(rumps.App):
    """The ONE system that rules them all"""
    
    def __init__(self):
        # Initialize menu bar with pig icon
        super(TinkyBinkMasterSystem, self).__init__("🐷", quit_button=None)
        
        # Paths
        self.home = Path.home()
        self.config_dir = self.home / ".claude"
        self.config_dir.mkdir(exist_ok=True)
        self.status_file = self.config_dir / "upload_status.txt"
        self.screenshot_config = self.config_dir / "screenshot_config.json"
        
        # State
        self.current_project = "General"
        self.screenshot_path = None
        self.upload_mode = False
        self.pressed_keys = set()
        
        # Components
        self.keyboard_listener = None
        self.mouse_listener = None
        self.screenshot_observer = None
        self.green_dot_timer = None
        
        # Status icons
        self.icons = {
            "ready": "🐷",
            "processing": "🐷🟡", 
            "uploading": "🐷⬆️",
            "error": "🐷❌",
            "success": "🐷✅"
        }
        
        # Hotkeys
        self.hotkeys = {
            'cmd_shift_0': {keyboard.Key.cmd, keyboard.Key.shift, keyboard.KeyCode.from_char('0')},
            'cmd_shift_9': {keyboard.Key.cmd, keyboard.Key.shift, keyboard.KeyCode.from_char('9')},
            'cmd_shift_8': {keyboard.Key.cmd, keyboard.Key.shift, keyboard.KeyCode.from_char('8')}
        }
        
        # Terminal submenu (dynamically populated)
        self.terminals_menu = rumps.MenuItem("🖥️ Terminal Mapping", callback=self.show_terminal_window)
        
        # Menu items
        self.menu = [
            rumps.MenuItem("🐷 TinkyBink Master System", callback=None),
            rumps.separator,
            rumps.MenuItem("Status: Enabled ✅", callback=None),  # Status enabled/disabled
            rumps.MenuItem(f"📁 Project: {self.current_project}", callback=None),  # Current project
            rumps.separator,
            self.terminals_menu,  # Terminal mapping submenu
            rumps.separator,
            rumps.MenuItem("📸 Cmd+Shift+0: Smart Upload", callback=None),
            rumps.MenuItem("🔥 Cmd+Shift+9: Terminal → File", callback=None),
            rumps.MenuItem("📝 Cmd+Shift+8: Terminal → TextEdit", callback=None),
            rumps.separator,
            rumps.MenuItem("⚙️ Settings", self.show_settings),
            rumps.MenuItem("♻️ Restart System", self.restart_system),
            rumps.MenuItem("🛑 Stop System", self.stop_system),
            rumps.separator,
            rumps.MenuItem("Quit", self.quit_application)
        ]
        
        # Start everything
        self.start_all_components()
        
        print("🐷 TINKYBINK MASTER SYSTEM STARTED")
        print("=" * 40)
        print("Everything unified in ONE system!")
        
    def start_all_components(self):
        """Start all system components"""
        # 1. Start keyboard listener
        self.start_keyboard_listener()
        
        # 2. Start screenshot watcher
        self.start_screenshot_watcher()
        
        # 3. Start green dot updater
        self.start_green_dot_updater()
        
        # 4. Update project folder
        self.update_current_project()
        
        # 5. Initialize terminals menu
        self.update_terminals_menu()
        
        # Set ready status
        self.set_status("ready")
        
    def set_status(self, status):
        """Update menu bar icon and status"""
        self.title = self.icons.get(status, "🐷")
        
        # Don't update the "Status: Enabled" menu item for operational statuses
        # Just update the icon
            
        # Flash success then back to ready
        if status == "success":
            threading.Timer(2.0, lambda: self.set_status("ready")).start()
            
    def set_system_status(self, enabled):
        """Update system enabled/disabled status"""
        for item in self.menu:
            if hasattr(item, 'title') and isinstance(item.title, str) and item.title.startswith("Status:"):
                item.title = "Status: Enabled ✅" if enabled else "Status: Disabled ❌"
                break
            
    def update_current_project(self):
        """Update current project from terminal or config"""
        try:
            found_project = False
            
            # Check for front terminal window
            script = '''
            tell application "Terminal"
                if (count of windows) > 0 then
                    set frontWindow to front window
                    try
                        set windowTitle to custom title of frontWindow
                        if windowTitle is not "" then
                            return windowTitle
                        end if
                    on error
                    end try
                end if
                return ""
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True)
            
            if result.stdout:
                title = result.stdout.strip()
                if title:
                    # Remove any dots from the title
                    if title.startswith("🟢 "):
                        title = title.replace("🟢 ", "", 1)
                    elif title.startswith("⚫ "):
                        title = title.replace("⚫ ", "", 1)
                    
                    # Use the clean title as the project name
                    if title and title != "":
                        self.current_project = title
                        found_project = True
            
            if not found_project:
                # No mapped terminal, check config or default
                if self.screenshot_config.exists():
                    with open(self.screenshot_config) as f:
                        config = json.load(f)
                        self.current_project = config.get("active_folder", "General")
                else:
                    self.current_project = "General"
                    
            # Update menu
            for item in self.menu:
                if hasattr(item, 'title') and isinstance(item.title, str) and item.title.startswith("📁 Project:"):
                    item.title = f"📁 Project: {self.current_project}"
                    break
                
        except Exception as e:
            print(f"Project update error: {e}")
            self.current_project = "No Project"
            # Still update menu on error
            for item in self.menu:
                if hasattr(item, 'title') and isinstance(item.title, str) and item.title.startswith("📁 Project:"):
                    item.title = f"📁 Project: {self.current_project}"
                    break
            
    # === KEYBOARD HANDLING ===
    
    def start_keyboard_listener(self):
        """Start listening for hotkeys"""
        def on_press(key):
            self.pressed_keys.add(key)
            
            # Check hotkeys
            if self.hotkeys['cmd_shift_0'].issubset(self.pressed_keys):
                self.handle_smart_upload()
                self.pressed_keys.clear()
            elif self.hotkeys['cmd_shift_9'].issubset(self.pressed_keys):
                self.handle_terminal_capture()
                self.pressed_keys.clear()
            elif self.hotkeys['cmd_shift_8'].issubset(self.pressed_keys):
                self.handle_textedit_capture()
                self.pressed_keys.clear()
                
        def on_release(key):
            self.pressed_keys.discard(key)
            
        self.keyboard_listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        self.keyboard_listener.start()
        
    def handle_smart_upload(self):
        """Handle Cmd+Shift+0 - Screenshot with auto-upload"""
        print("\n📸 Smart Upload triggered")
        self.set_status("processing")
        
        # Update project
        self.update_current_project()
        
        # Take screenshot in thread
        thread = threading.Thread(target=self._take_screenshot_and_upload)
        thread.daemon = True
        thread.start()
        
    def _take_screenshot_and_upload(self):
        """Take screenshot and prepare for upload"""
        try:
            # Create project folder
            screenshot_dir = self.home / "Desktop" / "App_Images" / self.current_project / "screenshots"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = screenshot_dir / filename
            
            # Take screenshot
            temp_path = Path("/tmp") / filename
            result = subprocess.run([
                'screencapture', '-i', '-x', str(temp_path)
            ], capture_output=True)
            
            if not temp_path.exists():
                print("Screenshot cancelled")
                self.set_status("ready")
                return
                
            # Move to project folder
            shutil.move(str(temp_path), str(filepath))
            self.screenshot_path = filepath
            
            print(f"✅ Saved: {self.current_project}/{filename}")
            
            # Enable upload mode
            self.enable_upload_mode()
            
            # Notification
            rumps.notification(
                title=f"Screenshot Ready",
                subtitle=f"Project: {self.current_project}",
                message="Click anywhere to upload"
            )
            
        except Exception as e:
            print(f"Screenshot error: {e}")
            self.set_status("error")
            
    def enable_upload_mode(self):
        """Enable click-to-upload"""
        self.upload_mode = True
        
        if not self.mouse_listener:
            self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
            self.mouse_listener.start()
            
        # Auto-disable after 15 seconds
        threading.Timer(15.0, self.disable_upload_mode).start()
        
    def disable_upload_mode(self):
        """Disable upload mode"""
        self.upload_mode = False
        
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse clicks for upload"""
        if not pressed or not self.upload_mode or not self.screenshot_path:
            return
            
        if button != mouse.Button.left:
            return
            
        time.sleep(0.3)
        self.perform_upload()
        self.upload_mode = False
        
    def perform_upload(self):
        """Upload the screenshot"""
        try:
            self.set_status("uploading")
            
            # Put file in pasteboard
            pasteboard = NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            file_url = NSURL.fileURLWithPath_(str(self.screenshot_path))
            pasteboard.writeObjects_([file_url])
            
            # Paste
            subprocess.run([
                'osascript', '-e',
                'tell application "System Events" to keystroke "v" using {command down, option down}'
            ])
            
            time.sleep(0.3)
            
            subprocess.run([
                'osascript', '-e',
                'tell application "System Events" to keystroke "v" using command down'
            ])
            
            print("✅ Upload complete!")
            self.set_status("success")
            
        except Exception as e:
            print(f"Upload error: {e}")
            self.set_status("error")
            
    def handle_terminal_capture(self):
        """Handle Cmd+Shift+9"""
        print("🔥 Terminal capture to file")
        subprocess.Popen(['python3', '/Users/lukekist/terminal_window_selector.py'])
        
    def handle_textedit_capture(self):
        """Handle Cmd+Shift+8"""
        print("📝 Terminal capture to TextEdit")
        subprocess.Popen(['python3', '/Users/lukekist/terminal_capture_to_textedit.py'])
        
    # === SCREENSHOT WATCHER ===
    
    def start_screenshot_watcher(self):
        """Watch desktop for screenshots to route"""
        print(f"📸 Starting screenshot watcher on: {self.home / 'Desktop'}")
        
        class ScreenshotHandler(FileSystemEventHandler):
            def __init__(self, master):
                self.master = master
                print(f"📱 Screenshot handler initialized")
                
            def on_created(self, event):
                if event.is_directory:
                    return
                    
                # Check if it's a screenshot
                filename = os.path.basename(event.src_path)
                print(f"📄 File created: {filename}")
                
                if filename.startswith(('.Screenshot', 'Screenshot', 'Screen Shot')):
                    print(f"📸 Screenshot detected: {filename}")
                    self.master.route_screenshot(event.src_path)
                else:
                    print(f"📄 Not a screenshot: {filename}")
                    
        handler = ScreenshotHandler(self)
        self.screenshot_observer = Observer()
        self.screenshot_observer.schedule(handler, str(self.home / "Desktop"), recursive=False)
        self.screenshot_observer.start()
        print(f"✅ Screenshot watcher started successfully")
        
    def route_screenshot(self, filepath):
        """Route screenshot to project folder"""
        try:
            print(f"📸 Processing screenshot: {filepath}")
            self.update_current_project()
            print(f"📁 Current project: {self.current_project}")
            
            # Create destination
            dest_dir = self.home / "Desktop" / "App_Images" / self.current_project / "screenshots"
            dest_dir.mkdir(parents=True, exist_ok=True)
            print(f"📂 Destination: {dest_dir}")
            
            # Move file
            filename = os.path.basename(filepath)
            dest_path = dest_dir / filename
            
            time.sleep(0.5)  # Let file finish writing
            shutil.move(filepath, str(dest_path))
            print(f"✅ Moved to: {dest_path}")
            
            # Show notification with project
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"📢 Sending notification...")
            
            try:
                rumps.notification(
                    title=f"[{self.current_project}] Screenshot",
                    subtitle=f"Captured at {timestamp}",
                    message=str(dest_path)
                )
                print(f"📱 Notification sent successfully")
            except Exception as notif_error:
                print(f"❌ Notification failed: {notif_error}")
                # Fallback to system notification
                subprocess.run([
                    'osascript', '-e',
                    f'display notification "Screenshot routed to {self.current_project}" with title "📸 Smart Router" sound name "Glass"'
                ], check=False)
                print(f"🔔 Fallback notification sent")
            
            print(f"[{self.current_project}] Screenshot routed: {filename}")
            
            # Auto-upload the screenshot
            print(f"🚀 Starting auto-upload...")
            self.screenshot_path = dest_path
            self.perform_upload()
            
        except Exception as e:
            print(f"❌ Routing error: {e}")
            
    # === GREEN DOT UPDATER ===
    
    def start_green_dot_updater(self):
        """Update dots on ALL terminals - green for active, black for inactive"""
        def update_dots():
            last_front_id = None
            while True:
                try:
                    # First get the current front window ID
                    get_front_script = '''
                    tell application "Terminal"
                        if (count of windows) > 0 then
                            return id of front window
                        end if
                        return 0
                    end tell
                    '''
                    result = subprocess.run(['osascript', '-e', get_front_script], 
                                          capture_output=True, text=True)
                    
                    if result.stdout:
                        current_front_id = result.stdout.strip()
                        
                        # Update every 2 seconds OR when front window changes
                        if True:  # Always update to ensure all terminals have dots
                            # Update all windows
                            update_script = f'''
                            tell application "Terminal"
                                repeat with w in windows
                                    set windowId to id of w as string
                                    
                                    -- Check if window has a custom title already
                                    set hasCustomTitle to false
                                    set currentTitle to ""
                                    try
                                        set currentTitle to custom title of w
                                        if currentTitle is not "" then
                                            set hasCustomTitle to true
                                        end if
                                    on error
                                        set hasCustomTitle to false
                                    end try
                                    
                                    -- Only update windows that have custom titles (mapped terminals)
                                    if hasCustomTitle then
                                        -- Clean up title (remove any existing dots)
                                        if currentTitle starts with "🟢 " then
                                            set currentTitle to text 3 thru -1 of currentTitle
                                        else if currentTitle starts with "⚫ " then
                                            set currentTitle to text 3 thru -1 of currentTitle
                                        end if
                                        
                                        -- Add appropriate dot based on if it's front window
                                        if windowId is "{current_front_id}" then
                                            set custom title of w to "🟢 " & currentTitle
                                        else
                                            set custom title of w to "⚫ " & currentTitle
                                        end if
                                        
                                        set title displays custom title of w to true
                                    end if
                                end repeat
                            end tell
                            '''
                            subprocess.run(['osascript', '-e', update_script], capture_output=True)
                            last_front_id = current_front_id
                    
                    # Also update the current project in menu
                    self.update_current_project()
                    
                    # Update terminals submenu
                    self.update_terminals_menu()
                    
                except Exception:
                    pass
                    
                time.sleep(2)
                
        thread = threading.Thread(target=update_dots, daemon=True)
        thread.start()
        
    def show_terminal_window(self, _):
        """Show window with all terminals for mapping"""
        try:
            # Get all terminal windows
            script = '''
            tell application "Terminal"
                set terminalInfo to ""
                set windowCount to count of windows
                
                repeat with i from 1 to windowCount
                    set w to window i
                    set windowId to id of w
                    set windowTitle to name of w
                    
                    -- Get custom title if exists
                    set customTitle to ""
                    try
                        set customTitle to custom title of w
                    on error
                        set customTitle to ""
                    end try
                    
                    if customTitle is not "" then
                        set terminalInfo to terminalInfo & windowId & "|" & customTitle & "|mapped" & "\n"
                    else
                        set terminalInfo to terminalInfo & windowId & "|" & windowTitle & "|unmapped" & "\n"
                    end if
                end repeat
                
                return terminalInfo
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True)
            
            # Build terminal list for display
            terminal_list = "=== CLICK ON A TERMINAL NUMBER TO RENAME ===\n\n"
            terminal_data = []
            
            if result.stdout:
                terminals = result.stdout.strip().split('\n')
                for i, terminal_info in enumerate(terminals, 1):
                    if terminal_info:
                        parts = terminal_info.split('|')
                        if len(parts) >= 3:
                            window_id = parts[0]
                            title = parts[1]
                            status = parts[2]
                            
                            # Create icon based on status
                            if i == 1:
                                icon = "🟢"  # Active terminal
                            elif status == "mapped":
                                icon = "✅"  # Mapped
                            else:
                                icon = "⚪"  # Not mapped
                            
                            terminal_list += f"{i}. {icon} {title}\n"
                            terminal_data.append((window_id, title))
            else:
                terminal_list += "No terminals found\n"
            
            terminal_list += "\n=== PROJECT FOLDERS ===\n"
            
            # Show project folders
            app_images = self.home / "Desktop" / "App_Images"
            if app_images.exists():
                for folder in sorted(app_images.iterdir()):
                    if folder.is_dir():
                        if folder.name == self.current_project:
                            terminal_list += f"📂 {folder.name} ← ACTIVE\n"
                        else:
                            terminal_list += f"📁 {folder.name}\n"
            
            terminal_list += f"\n=== CURRENT STATUS ===\n"
            terminal_list += f"Active Project: {self.current_project}\n"
            terminal_list += f"Screenshots Route To: ~/Desktop/App_Images/{self.current_project}/\n"
            terminal_list += "\nEnter terminal number (1, 2, 3...) to rename:"
            
            # Show window asking which terminal to rename
            response = rumps.Window(
                title="🖥️ Terminal Mapping",
                message=terminal_list,
                default_text="",
                ok="Select",
                cancel="Close"
            ).run()
            
            if response.clicked:
                try:
                    # Get the terminal number
                    terminal_num = int(response.text.strip())
                    if 1 <= terminal_num <= len(terminal_data):
                        window_id, current_title = terminal_data[terminal_num - 1]
                        self.rename_terminal(window_id, current_title)
                except ValueError:
                    rumps.alert("Invalid Input", "Please enter a terminal number")
                    
        except Exception as e:
            rumps.alert("Error", f"Could not show terminals: {e}")
    
    def update_terminals_menu(self):
        """Update the terminals submenu (no longer used for submenu)"""
        # This method is now just a placeholder since we're using a click handler
        pass
            
    def rename_terminal(self, window_id, current_title):
        """Rename a specific terminal window"""
        try:
            # Clean up current title for display
            display_title = current_title
            if "—" in current_title:
                parts = current_title.split("—")
                if len(parts) > 1:
                    display_title = parts[1].strip()
            
            # Show rename dialog
            response = rumps.Window(
                title="Rename Terminal",
                message=f"Enter new name for terminal:",
                default_text=display_title,
                ok="Rename",
                cancel="Cancel"
            ).run()
            
            if response.clicked:
                new_name = response.text.strip()
                if new_name:
                    # Apply the new name
                    script = f'''
                    tell application "Terminal"
                        repeat with w in windows
                            if (id of w) is {window_id} then
                                set custom title of w to "{new_name}"
                                set title displays custom title of w to true
                                return "success"
                            end if
                        end repeat
                    end tell
                    '''
                    
                    result = subprocess.run(['osascript', '-e', script],
                                          capture_output=True, text=True)
                    
                    if result.stdout and "success" in result.stdout:
                        rumps.notification(
                            title="Terminal Renamed",
                            subtitle=f"New name: {new_name}",
                            message="Terminal mapping updated"
                        )
                        
                        # Update the menu immediately
                        self.update_terminals_menu()
                        self.update_current_project()
                    
        except Exception as e:
            print(f"Error renaming terminal: {e}")
        
    # === MENU ACTIONS ===
    
    def show_settings(self, _):
        """Show settings dialog"""
        rumps.alert(
            title="TinkyBink Settings",
            message=f"Current Project: {self.current_project}\n"
                   f"Screenshots: ~/Desktop/App_Images/{self.current_project}/\n\n"
                   "Hotkeys:\n"
                   "📸 Cmd+Shift+0: Smart Upload\n"
                   "🔥 Cmd+Shift+9: Terminal to File\n"
                   "📝 Cmd+Shift+8: Terminal to TextEdit"
        )
        
    def restart_system(self, _):
        """Restart the system"""
        rumps.notification(
            title="Restarting System",
            subtitle="TinkyBink Master System",
            message="System will restart now..."
        )
        
        # Restart self
        os.execv(sys.executable, [sys.executable] + sys.argv)
        
    def stop_system(self, _):
        """Stop the system"""
        rumps.notification(
            title="System Stopped",
            subtitle="TinkyBink Master System",
            message="All components stopped"
        )
        
        # Stop components
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.screenshot_observer:
            self.screenshot_observer.stop()
            
        # Update status
        self.set_status("ready")
        
    def quit_application(self, _):
        """Quit everything"""
        self.stop_system(None)
        rumps.quit_application()

def main():
    """Start the master system"""
    # Kill any old processes
    os.system("pkill -f 'smart_screenshot_router|unified_hotkey|menu_bar_indicator|auto_green_dot|option_click'")
    time.sleep(1)
    
    # Start the ONE system
    app = TinkyBinkMasterSystem()
    app.run()

if __name__ == "__main__":
    main()