#!/usr/bin/env python3
"""
Menu Bar Status Indicator for Upload System
Shows colored overlay: Yellow (processing), Red (error), Green (ready)
"""

import os
import sys
import time
import threading
from pathlib import Path

try:
    import rumps
    from AppKit import NSColor, NSImage, NSMakeRect, NSBezierPath, NSCompositingOperationSourceOver
except ImportError:
    print("Installing rumps for menu bar...")
    os.system("pip3 install rumps pyobjc-framework-Cocoa")
    import rumps
    from AppKit import NSColor, NSImage, NSMakeRect, NSBezierPath, NSCompositingOperationSourceOver

class UploadStatusIndicator(rumps.App):
    def __init__(self):
        super(UploadStatusIndicator, self).__init__("🐷", quit_button=None)
        
        self.status_file = Path.home() / ".claude" / "upload_status.txt"
        self.status_file.parent.mkdir(exist_ok=True)
        
        # Status states with pig variations
        self.states = {
            "ready": "🐷",      # Normal pig - idle/ready
            "processing": "🐷🟡",  # Pig with yellow - taking screenshot/processing
            "uploading": "🐷⬆️",   # Pig with up arrow - uploading
            "error": "🐷❌",       # Pig with X - error/broken
            "success": "🐷✅"      # Pig with check - briefly shown
        }
        
        self.current_state = "ready"
        self.monitor_thread = None
        
        # Create menu items
        self.menu = [
            rumps.MenuItem("📸 Cmd+Shift+0: Smart Upload", callback=None),
            rumps.MenuItem("🔥 Cmd+Shift+9: Terminal → File", callback=None),
            rumps.MenuItem("📝 Cmd+Shift+8: Terminal → TextEdit", callback=None),
            rumps.separator,
            rumps.MenuItem("Status: Ready", callback=None),
            rumps.separator,
            rumps.MenuItem("Restart System", self.restart_system),
            rumps.MenuItem("Stop System", self.stop_system),
            rumps.separator,
            rumps.MenuItem("Quit Menu Bar", self.quit_application)
        ]
        
        # Start monitoring
        self.start_monitoring()
        
    def start_monitoring(self):
        """Monitor status file for changes"""
        def monitor():
            while True:
                try:
                    # Check status file
                    if self.status_file.exists():
                        with open(self.status_file, 'r') as f:
                            status = f.read().strip()
                            
                        if status != self.current_state:
                            self.update_status(status)
                            
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.update_status("error")
                    time.sleep(1)
                    
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
        
    def update_status(self, status):
        """Update the menu bar icon and status"""
        self.current_state = status
        
        # Update icon
        if status in self.states:
            self.title = self.states[status]
        else:
            self.title = "🐷"
            
        # Update status menu item
        status_text = {
            "ready": "Status: Ready",
            "processing": "Status: Taking Screenshot...",
            "uploading": "Status: Uploading...",
            "error": "Status: Error - Restart System",
            "success": "Status: Upload Complete!"
        }.get(status, "Status: Unknown")
        
        # Update the status menu item
        if len(self.menu) > 4:
            self.menu[4].title = status_text
            
        # Flash success briefly
        if status == "success":
            threading.Timer(2.0, lambda: self.update_status("ready")).start()
            
    def restart_system(self, _):
        """Restart the upload system"""
        try:
            os.system("pkill -f 'unified_hotkey|global_hotkey'")
            time.sleep(1)
            os.system("nohup python3 /Users/lukekist/unified_hotkey_system.py > ~/.claude/unified.log 2>&1 &")
            
            rumps.notification(
                title="System Restarted",
                subtitle="Upload system is ready",
                message="Press Cmd+Shift+0 to capture and upload"
            )
            
            self.update_status("ready")
            
        except Exception as e:
            self.update_status("error")
    
    def stop_system(self, _):
        """Stop the hotkey system only"""
        try:
            os.system("pkill -f 'unified_hotkey'")
            
            rumps.notification(
                title="System Stopped",
                subtitle="Hotkey system has been stopped",
                message="Use 'Restart System' to start again"
            )
            
            self.update_status("ready")
            
        except Exception as e:
            self.update_status("error")
            
    def quit_application(self, _):
        """Quit the menu bar application"""
        # Stop the hotkey system too
        os.system("pkill -f 'unified_hotkey'")
        rumps.quit_application()

def write_status(status):
    """Helper function to write status from other scripts"""
    status_file = Path.home() / ".claude" / "upload_status.txt"
    status_file.parent.mkdir(exist_ok=True)
    with open(status_file, 'w') as f:
        f.write(status)

if __name__ == "__main__":
    # Initialize with ready status
    write_status("ready")
    
    # Start the app
    app = UploadStatusIndicator()
    app.run()