#!/usr/bin/env python3
"""
⌥ OPTION+CLICK RENAME - Hold Option and click to rename terminals
Simple and native feeling - just like macOS file renaming
"""

import time
import subprocess
from pynput import mouse, keyboard
from pynput.keyboard import Key
import threading
import queue

class OptionClickRename:
    def __init__(self):
        self.option_pressed = False
        self.rename_queue = queue.Queue()
        self.running = True
        
        print("⌥ OPTION+CLICK RENAME SYSTEM")
        print("============================")
        print("🎯 Hold Option key + click on terminal to rename")
        print("🖱️ Just like renaming files in Finder!")
        print("Press Ctrl+C to stop")
        
    def on_key_press(self, key):
        """Detect when Option key is pressed"""
        try:
            if key == Key.alt or key == Key.alt_l or key == Key.alt_r:
                if not self.option_pressed:
                    self.option_pressed = True
                    print("⌥ Option key held - ready for click")
        except AttributeError:
            pass
    
    def on_key_release(self, key):
        """Detect when Option key is released"""
        try:
            if key == Key.alt or key == Key.alt_l or key == Key.alt_r:
                if self.option_pressed:
                    self.option_pressed = False
                    print("⚫ Option key released")
        except AttributeError:
            pass
    
    def on_click(self, x, y, button, pressed):
        """Handle mouse clicks when Option is held"""
        if pressed and button == mouse.Button.left and self.option_pressed:
            print(f"🎯 Option+Click detected at ({x}, {y})")
            
            # Check if we clicked on a terminal window
            terminal_info = self.get_terminal_at_position(x, y)
            if terminal_info:
                print(f"✅ Terminal found: {terminal_info['name']}")
                # Add to queue for processing
                self.rename_queue.put(terminal_info)
            else:
                print("❌ No terminal at click position")
    
    def get_terminal_at_position(self, x, y):
        """Get terminal window info at the clicked position"""
        try:
            script = f'''
            tell application "Terminal"
                repeat with w in windows
                    try
                        set windowBounds to bounds of w
                        set windowName to name of w
                        set windowId to id of w
                        
                        -- Check if click is within window bounds
                        set leftBound to item 1 of windowBounds
                        set topBound to item 2 of windowBounds
                        set rightBound to item 3 of windowBounds
                        set bottomBound to item 4 of windowBounds
                        
                        if {x} >= leftBound and {x} <= rightBound and {y} >= topBound and {y} <= bottomBound then
                            return windowId & "|" & windowName
                        end if
                    on error
                    end try
                end repeat
                return "none"
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output and output != "none":
                    parts = output.split("|", 1)
                    if len(parts) == 2:
                        return {
                            'id': parts[0],
                            'name': parts[1]
                        }
            
            return None
            
        except Exception as e:
            print(f"❌ Position detection error: {e}")
            return None
    
    def rename_terminal(self, terminal_info):
        """Show rename dialog and update terminal"""
        try:
            current_name = terminal_info['name']
            window_id = terminal_info['id']
            
            # Extract just the custom title part if it exists
            display_name = current_name
            if " — " in current_name:
                parts = current_name.split(" — ")
                if len(parts) > 1:
                    display_name = parts[1]  # Get the part after the username
            
            # Show input dialog with current name
            script = f'''
            set currentName to "{display_name}"
            set dialogResult to display dialog "⌥ Rename Terminal:" default answer currentName with title "Option+Click Rename" buttons {{"Cancel", "Rename"}} default button "Rename"
            set newName to text returned of dialogResult
            
            if newName is not "" then
                tell application "Terminal"
                    repeat with w in windows
                        if (id of w) is {window_id} then
                            set custom title of w to newName
                            set title displays custom title of w to true
                            return "success|" & newName
                        end if
                    end repeat
                end tell
            end if
            return "cancelled"
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output.startswith("success|"):
                    new_name = output.split("|", 1)[1]
                    print(f"✅ Terminal renamed to: {new_name}")
                    
                    # Show notification
                    subprocess.run([
                        'osascript', '-e',
                        f'display notification "Terminal renamed to {new_name}" with title "⌥ Option+Click" sound name "Glass"'
                    ], check=False)
                    
                    return True
                else:
                    print("❌ Rename cancelled")
            
            return False
            
        except Exception as e:
            print(f"❌ Rename error: {e}")
            return False
    
    def process_rename_queue(self):
        """Process rename requests in background"""
        while self.running:
            try:
                if not self.rename_queue.empty():
                    terminal_info = self.rename_queue.get(timeout=1)
                    self.rename_terminal(terminal_info)
                else:
                    time.sleep(0.1)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Queue error: {e}")
    
    def start_monitoring(self):
        """Start the Option+Click monitoring system"""
        # Start rename queue processor in background
        rename_thread = threading.Thread(target=self.process_rename_queue, daemon=True)
        rename_thread.start()
        
        # Start keyboard and mouse listeners
        keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        
        mouse_listener = mouse.Listener(
            on_click=self.on_click
        )
        
        keyboard_listener.start()
        mouse_listener.start()
        
        print("\n🎯 OPTION+CLICK SYSTEM ACTIVE!")
        print("Hold Option key and click on any terminal to rename it")
        print("Works just like renaming files in Finder! 🖱️")
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n👋 Option+Click rename system stopped")
            self.running = False
            keyboard_listener.stop()
            mouse_listener.stop()

def main():
    """Run the Option+Click rename system"""
    renamer = OptionClickRename()
    renamer.start_monitoring()

if __name__ == "__main__":
    main()