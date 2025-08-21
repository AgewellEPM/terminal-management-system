#!/usr/bin/env python3
"""
📁 SET SCREENSHOT FOLDER - Choose where screenshots go
Lets you set custom folder names for screenshot routing
"""

import subprocess
import json
from pathlib import Path

class ScreenshotFolderManager:
    def __init__(self):
        self.config_file = Path.home() / ".claude" / "screenshot_config.json"
        self.config_file.parent.mkdir(exist_ok=True)
        self.base_dir = Path.home() / "Desktop" / "App_Images"
        
    def load_config(self):
        """Load current screenshot routing configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        return {"active_folder": "Terminal", "folders": ["Terminal"]}
    
    def save_config(self, config):
        """Save screenshot routing configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Config save error: {e}")
            return False
    
    def list_existing_folders(self):
        """List existing project folders"""
        try:
            if self.base_dir.exists():
                folders = [d.name for d in self.base_dir.iterdir() if d.is_dir()]
                return sorted(folders)
        except:
            pass
        return []
    
    def create_folder(self, folder_name):
        """Create a new project folder"""
        try:
            folder_path = self.base_dir / folder_name / "screenshots"
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created folder: {folder_path}")
            return True
        except Exception as e:
            print(f"❌ Folder creation error: {e}")
            return False
    
    def set_active_folder(self, folder_name):
        """Set the active folder for screenshot routing"""
        config = self.load_config()
        
        # Create folder if it doesn't exist
        if not self.create_folder(folder_name):
            return False
        
        # Update config
        config["active_folder"] = folder_name
        if folder_name not in config.get("folders", []):
            config.setdefault("folders", []).append(folder_name)
        
        if self.save_config(config):
            # Update terminal title with new folder
            self.update_terminal_title(folder_name)
            
            # Show notification
            subprocess.run([
                'osascript', '-e',
                f'display notification "Screenshots will route to {folder_name}" with title "📁 Folder Set" sound name "Glass"'
            ], check=False)
            
            print(f"✅ Active screenshot folder set to: {folder_name}")
            print(f"📁 Path: ~/Desktop/App_Images/{folder_name}/screenshots/")
            return True
        
        return False
    
    def update_terminal_title(self, folder_name):
        """Update terminal title with active folder"""
        try:
            title = f"🟢 {folder_name} | SCREENSHOT TARGET"
            
            script = f'''
            tell application "Terminal"
                set custom title of front window to "{title}"
                set title displays custom title of front window to true
            end tell
            '''
            
            subprocess.run(['osascript', '-e', script], check=False)
            
        except Exception as e:
            print(f"❌ Title update error: {e}")
    
    def show_menu(self):
        """Show interactive folder selection menu"""
        config = self.load_config()
        existing_folders = self.list_existing_folders()
        
        print("📁 SCREENSHOT FOLDER MANAGER")
        print("============================")
        print(f"🎯 Current active folder: {config.get('active_folder', 'None')}")
        print()
        
        if existing_folders:
            print("📋 Existing folders:")
            for i, folder in enumerate(existing_folders, 1):
                marker = "🎯" if folder == config.get('active_folder') else "📁"
                print(f"  {i}. {marker} {folder}")
            print()
        
        print("💡 Options:")
        print("  • Type folder name to create/switch to it")
        print("  • Type number to switch to existing folder")
        print("  • Type 'list' to see all folders")
        print("  • Type 'quit' to exit")
        print()
        
        while True:
            try:
                choice = input("📁 Enter folder name or number: ").strip()
                
                if choice.lower() == 'quit':
                    break
                elif choice.lower() == 'list':
                    self.show_folder_contents()
                    continue
                elif choice.isdigit() and existing_folders:
                    idx = int(choice) - 1
                    if 0 <= idx < len(existing_folders):
                        folder_name = existing_folders[idx]
                        self.set_active_folder(folder_name)
                        break
                    else:
                        print("❌ Invalid number")
                        continue
                elif choice:
                    # Clean folder name
                    folder_name = choice.replace(" ", "_").replace("/", "_")
                    self.set_active_folder(folder_name)
                    break
                else:
                    print("❌ Please enter a folder name")
                    
            except KeyboardInterrupt:
                print("\n👋 Cancelled")
                break
    
    def show_folder_contents(self):
        """Show contents of existing folders"""
        existing_folders = self.list_existing_folders()
        
        print("\n📊 FOLDER CONTENTS:")
        print("===================")
        
        for folder in existing_folders:
            folder_path = self.base_dir / folder / "screenshots"
            if folder_path.exists():
                screenshot_count = len(list(folder_path.glob("*.png")))
                print(f"📁 {folder}: {screenshot_count} screenshots")
            else:
                print(f"📁 {folder}: (empty)")
        print()

def main():
    """Run screenshot folder manager"""
    import sys
    
    manager = ScreenshotFolderManager()
    
    if len(sys.argv) > 1:
        # Command line usage
        folder_name = " ".join(sys.argv[1:]).replace(" ", "_")
        manager.set_active_folder(folder_name)
    else:
        # Interactive menu
        manager.show_menu()

if __name__ == "__main__":
    main()