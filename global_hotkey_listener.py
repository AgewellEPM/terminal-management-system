#!/usr/bin/env python3
"""
⌨️ GLOBAL HOTKEY LISTENER - Command+Shift+9
Listens for Command+Shift+9 globally and triggers terminal window selector
"""

import subprocess
from pynput import keyboard
import threading
import time

class GlobalHotkeyListener:
    def __init__(self):
        self.pressed_keys = set()
        self.hotkey_combo_9 = {keyboard.Key.cmd, keyboard.Key.shift, keyboard.KeyCode.from_char('9')}
        self.hotkey_combo_8 = {keyboard.Key.cmd, keyboard.Key.shift, keyboard.KeyCode.from_char('8')}
        self.listener = None
        
    def on_key_press(self, key):
        """Handle key press events"""
        self.pressed_keys.add(key)
        
        # Check if Command+Shift+9 is pressed (save to files)
        if self.hotkey_combo_9.issubset(self.pressed_keys):
            print("🔥 Command+Shift+9 detected!")
            self.trigger_terminal_selector()
        
        # Check if Command+Shift+8 is pressed (open in TextEdit)
        elif self.hotkey_combo_8.issubset(self.pressed_keys):
            print("📝 Command+Shift+8 detected!")
            self.trigger_textedit_capture()
    
    def on_key_release(self, key):
        """Handle key release events"""
        try:
            self.pressed_keys.remove(key)
        except KeyError:
            pass
    
    def trigger_terminal_selector(self):
        """Launch the terminal window selector (Command+Shift+9)"""
        try:
            subprocess.run([
                'python3', '/Users/lukekist/terminal_window_selector.py'
            ], check=False)
        except Exception as e:
            print(f"❌ Failed to launch selector: {e}")
    
    def trigger_textedit_capture(self):
        """Launch the TextEdit capture (Command+Shift+8)"""
        try:
            subprocess.run([
                'python3', '/Users/lukekist/terminal_capture_to_textedit.py'
            ], check=False)
        except Exception as e:
            print(f"❌ Failed to launch TextEdit capture: {e}")
    
    def start_listening(self):
        """Start the global hotkey listener"""
        print("⌨️ GLOBAL HOTKEY LISTENER ACTIVE")
        print("=================================")
        print("🔥 Command+Shift+9: Capture terminal → Save to files")
        print("📝 Command+Shift+8: Capture terminal → Open in TextEdit")
        print("📸 Both show camera cursor for window selection")
        print("Press Ctrl+C to stop")
        print()
        
        with keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        ) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                print("\n👋 Hotkey listener stopped")

def main():
    """Run the global hotkey listener"""
    listener = GlobalHotkeyListener()
    listener.start_listening()

if __name__ == "__main__":
    main()