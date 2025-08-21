#!/usr/bin/env python3
"""
📸 SMART SCREENSHOT ROUTER - Routes to Active Terminal's Project
Routes screenshots to the project folder of whichever terminal has the green dot
"""

import os
import time
import shutil
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SmartScreenshotRouter(FileSystemEventHandler):
    def __init__(self):
        self.desktop = Path.home() / "Desktop"
        self.base_project_dir = Path.home() / "Desktop" / "App_Images"
        
        print("📸 SMART SCREENSHOT ROUTER STARTING")
        print("===================================")
        print(f"📂 Watching: {self.desktop}")
        print(f"📁 Routes to: {self.base_project_dir}/[ACTIVE_PROJECT]/screenshots/")
        print("🟢 Routes based on which terminal has the green dot")
        
    def get_active_project_from_config(self):
        """Get the active project from user configuration"""
        try:
            import json
            config_file = Path.home() / ".claude" / "screenshot_config.json"
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('active_folder', 'Terminal')
            
            return "Terminal"
            
        except Exception as e:
            print(f"❌ Config read error: {e}")
            return "Terminal"
    
    def get_active_terminal_project(self):
        """Get the project name - first check config, then green dot"""
        # Try user-configured folder first
        config_folder = self.get_active_project_from_config()
        
        # Also check for green dot terminal
        try:
            script = '''
            tell application "Terminal"
                repeat with w in windows
                    try
                        set windowTitle to custom title of w
                        if windowTitle contains "🟢" then
                            return windowTitle
                        end if
                    on error
                    end try
                end repeat
                return "no_green_dot"
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                title = result.stdout.strip()
                if title and title != "no_green_dot" and "🟢" in title:
                    # Extract project name from title
                    if "|" in title:
                        project_part = title.split("|")[0].strip()
                        green_dot_project = project_part.replace("🟢", "").strip()
                        # Use green dot project if it's different from config
                        if green_dot_project and green_dot_project != config_folder:
                            return green_dot_project
            
            return config_folder
            
        except Exception as e:
            print(f"❌ Project detection error: {e}")
            return config_folder
    
    def on_created(self, event):
        """Handle new files on Desktop"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        filename = file_path.name
        
        # Only handle screenshots
        if not ("Screenshot" in filename and filename.endswith('.png')):
            return
        
        print(f"📸 Screenshot detected: {filename}")
        
        # Wait for file to be complete
        time.sleep(0.5)
        
        # Get the active project
        project_name = self.get_active_terminal_project()
        
        # Create project directory structure
        project_dir = self.base_project_dir / project_name
        screenshots_dir = project_dir / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Move to project folder
        try:
            dest_path = screenshots_dir / filename
            shutil.move(str(file_path), str(dest_path))
            
            timestamp = time.strftime("%H:%M:%S")
            print(f"✅ [{timestamp}] Routed to: {project_name}")
            print(f"   📁 Path: {screenshots_dir}")
            
            # Show notification with project name
            subprocess.run([
                'osascript', '-e',
                f'display notification "Screenshot routed to {project_name}" with title "📸 Smart Router" sound name "Glass"'
            ], check=False)
            
        except Exception as e:
            print(f"❌ Error routing {filename}: {e}")
            # Fallback to default location
            fallback_dir = self.base_project_dir / "Screenshots"
            fallback_dir.mkdir(parents=True, exist_ok=True)
            try:
                dest_path = fallback_dir / filename
                shutil.move(str(file_path), str(dest_path))
                print(f"📁 Fallback: Moved to {fallback_dir}")
            except Exception as e2:
                print(f"❌ Fallback failed: {e2}")

def main():
    """Run the smart screenshot router"""
    router = SmartScreenshotRouter()
    
    # Setup file watcher
    observer = Observer()
    observer.schedule(router, str(router.desktop), recursive=False)
    observer.start()
    
    print("\n🎯 SMART ROUTER ACTIVE!")
    print("Screenshots will route to the project of the terminal with 🟢")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n👋 Smart router stopped")
    
    observer.join()

if __name__ == "__main__":
    main()