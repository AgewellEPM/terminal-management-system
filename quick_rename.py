#!/usr/bin/env python3
"""Quick terminal renaming tool"""

import subprocess
import sys

def rename_terminal(window_id, new_name):
    """Rename a terminal"""
    script = f'''
    tell application "Terminal"
        repeat with w in windows
            if (id of w) is {window_id} then
                set custom title of w to "{new_name}"
                set title displays custom title of w to true
                return "success"
            end if
        end repeat
        return "failed"
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return "success" in result.stdout

if len(sys.argv) != 3:
    print("Usage: python3 quick_rename.py TERMINAL_ID PROJECT_NAME")
    print("Example: python3 quick_rename.py 1773 TinkyBinkAAC")
    sys.exit(1)

window_id = sys.argv[1]
project_name = sys.argv[2]

print(f"🔄 Renaming terminal {window_id} to '{project_name}'...")

if rename_terminal(window_id, project_name):
    print(f"✅ Success! Terminal {window_id} is now '{project_name}'")
    print(f"📁 Screenshots will route to: ~/Desktop/App_Images/{project_name}/screenshots/")
    
    # Create the project folder
    from pathlib import Path
    project_dir = Path.home() / "Desktop" / "App_Images" / project_name / "screenshots"
    project_dir.mkdir(parents=True, exist_ok=True)
    print(f"📂 Created project folder: {project_dir}")
    
else:
    print(f"❌ Failed to rename terminal {window_id}")