#!/usr/bin/env python3
"""
🟢 AUTO GREEN DOT - Follows Your Focus Automatically
Green dot automatically moves to whichever terminal you're working in
"""

import subprocess
import time

class AutoGreenDot:
    def __init__(self):
        self.current_active_window = None
        print("🟢 AUTO GREEN DOT STARTING")
        print("==========================")
        print("🎯 Green dot will automatically follow your focus")
        
    def get_active_terminal_window(self):
        """Get the currently active terminal window ID"""
        try:
            script = '''
            tell application "System Events"
                try
                    set frontApp to first application process whose frontmost is true
                    if name of frontApp is "Terminal" then
                        tell application "Terminal"
                            return id of front window
                        end tell
                    else
                        return "not_terminal"
                    end if
                on error
                    return "error"
                end try
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output not in ["not_terminal", "error"]:
                    return output
            
            return None
            
        except Exception as e:
            print(f"❌ Detection error: {e}")
            return None
    
    def get_all_terminal_windows(self):
        """Get all open terminal windows"""
        try:
            script = '''
            tell application "Terminal"
                set windowList to {}
                repeat with w in windows
                    try
                        set end of windowList to (id of w)
                    on error
                    end try
                end repeat
                return windowList
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                # Parse the AppleScript list
                output = result.stdout.strip()
                if output and output != "{}":
                    # Extract numbers from the list format
                    import re
                    numbers = re.findall(r'\d+', output)
                    return numbers
            
            return []
            
        except Exception as e:
            print(f"❌ Window list error: {e}")
            return []
    
    def set_window_title(self, window_id, title, is_active=False):
        """Set title for a specific window"""
        try:
            if is_active:
                full_title = f"🟢 {title} | ACTIVE TARGET"
            else:
                full_title = f"⚫ {title}"
            
            script = f'''
            tell application "Terminal"
                repeat with w in windows
                    if (id of w) is {window_id} then
                        set custom title of w to "{full_title}"
                        set title displays custom title of w to true
                        return "success"
                    end if
                end repeat
                return "not_found"
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=False)
            
            return "success" in result.stdout
            
        except Exception as e:
            print(f"❌ Title set error: {e}")
            return False
    
    def get_project_name(self, window_id):
        """Get project name for a window (simplified)"""
        try:
            # For now, just use "Terminal" - you can enhance this later
            return "Terminal"
        except:
            return "Terminal"
    
    def update_all_terminals(self, active_window_id):
        """Update all terminal windows - green for active, regular for others"""
        try:
            all_windows = self.get_all_terminal_windows()
            
            for window_id in all_windows:
                project_name = self.get_project_name(window_id)
                is_active = (window_id == active_window_id)
                self.set_window_title(window_id, project_name, is_active)
            
            return True
            
        except Exception as e:
            print(f"❌ Update error: {e}")
            return False
    
    def monitor_focus(self):
        """Monitor terminal focus and update green dots"""
        print("🔍 Monitoring terminal focus...")
        print("🟢 Green dot will move automatically to active terminal")
        print("⚫ Inactive terminals will show regular dots")
        print("Press Ctrl+C to stop")
        print()
        
        while True:
            try:
                current_window = self.get_active_terminal_window()
                
                # Only update if focus changed
                if current_window and current_window != self.current_active_window:
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"🕐 [{timestamp}] Focus changed to window: {current_window}")
                    
                    # Update all terminal titles
                    if self.update_all_terminals(current_window):
                        print(f"✅ Green dot moved to active terminal")
                        
                        # Show notification
                        subprocess.run([
                            'osascript', '-e',
                            'display notification "Green dot moved to active terminal" with title "🟢 Focus Changed" sound name "Ping"'
                        ], check=False)
                    
                    self.current_active_window = current_window
                
                time.sleep(0.5)  # Check twice per second for responsive updates
                
            except KeyboardInterrupt:
                print("\n👋 Auto green dot stopped")
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(2)

def main():
    """Run the auto green dot system"""
    auto_dot = AutoGreenDot()
    auto_dot.monitor_focus()

if __name__ == "__main__":
    main()