#!/usr/bin/env python3
"""
🖥️ TERMINAL PROJECT MAPPER
Interactive tool to map each terminal to a project folder
"""

import subprocess
import time
from pathlib import Path

def get_all_terminals():
    """Get all terminal windows with their current info"""
    script = '''
    tell application "Terminal"
        set terminalList to {}
        repeat with w in windows
            set windowId to id of w
            set windowName to name of w
            
            -- Get custom title if exists
            set customTitle to ""
            try
                set customTitle to custom title of w
            on error
                set customTitle to ""
            end try
            
            -- Get current directory if possible
            set currentDir to ""
            try
                set currentDir to (do shell script "echo $PWD" in w)
            on error
                set currentDir to "~"
            end try
            
            set end of terminalList to (windowId as string) & "|" & windowName & "|" & customTitle & "|" & currentDir
        end repeat
        return terminalList
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    terminals = []
    
    if result.stdout:
        for line in result.stdout.strip().split(', '):
            if line and '|' in line:
                parts = line.split('|')
                if len(parts) >= 4:
                    window_id = parts[0]
                    window_name = parts[1]
                    custom_title = parts[2]
                    current_dir = parts[3]
                    
                    # Clean up custom title
                    display_title = custom_title
                    if display_title.startswith("🟢 "):
                        display_title = display_title[3:]
                    elif display_title.startswith("⚫ "):
                        display_title = display_title[3:]
                    
                    # Determine status
                    is_active = "🟢" in custom_title
                    has_custom = bool(display_title)
                    
                    terminals.append({
                        'id': window_id,
                        'name': window_name,
                        'custom_title': display_title,
                        'current_dir': current_dir,
                        'is_active': is_active,
                        'has_custom': has_custom
                    })
    
    return terminals

def show_existing_projects():
    """Show existing project folders"""
    app_images = Path.home() / "Desktop" / "App_Images"
    projects = []
    
    if app_images.exists():
        for folder in sorted(app_images.iterdir()):
            if folder.is_dir():
                screenshot_count = 0
                screenshot_dir = folder / "screenshots"
                if screenshot_dir.exists():
                    screenshot_count = len([f for f in screenshot_dir.iterdir() if f.suffix == '.png'])
                projects.append({
                    'name': folder.name,
                    'path': str(folder),
                    'screenshots': screenshot_count
                })
    
    return projects

def rename_terminal(window_id, new_name):
    """Rename a terminal window"""
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

def main():
    """Main mapping interface"""
    print("🖥️ ═══ TERMINAL PROJECT MAPPER ═══")
    print()
    
    while True:
        # Get current terminals
        terminals = get_all_terminals()
        projects = show_existing_projects()
        
        print("📋 CURRENT TERMINALS:")
        print("─" * 80)
        
        for i, terminal in enumerate(terminals, 1):
            status = "🟢 ACTIVE" if terminal['is_active'] else "⚫ inactive"
            mapped = "✅ mapped" if terminal['has_custom'] else "❌ unmapped"
            
            current_name = terminal['custom_title'] if terminal['custom_title'] else "No Project"
            dir_name = Path(terminal['current_dir']).name if terminal['current_dir'] != '~' else 'Home'
            
            print(f"{i:2d}. {status} │ {mapped} │ Project: {current_name}")
            print(f"     Window: {terminal['name']}")
            print(f"     Directory: {dir_name}")
            print()
        
        print("📁 EXISTING PROJECT FOLDERS:")
        print("─" * 50)
        for project in projects:
            print(f"📂 {project['name']} ({project['screenshots']} screenshots)")
        
        print("\n🎯 OPTIONS:")
        print("1-99: Rename terminal number")
        print("  s:  Show all info")
        print("  q:  Quit")
        
        choice = input("\n👉 Enter choice: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == 's':
            # Show detailed info
            print("\n" + "=" * 80)
            for terminal in terminals:
                print(f"ID: {terminal['id']}")
                print(f"Name: {terminal['name']}")
                print(f"Custom: {terminal['custom_title']}")
                print(f"Directory: {terminal['current_dir']}")
                print(f"Active: {terminal['is_active']}")
                print("-" * 40)
            input("Press Enter to continue...")
        elif choice.isdigit():
            terminal_num = int(choice)
            if 1 <= terminal_num <= len(terminals):
                terminal = terminals[terminal_num - 1]
                
                print(f"\n🔧 RENAMING TERMINAL {terminal_num}")
                print(f"Current: {terminal['custom_title'] or 'No Project'}")
                print(f"Directory: {terminal['current_dir']}")
                
                print("\n💡 SUGGESTIONS:")
                # Suggest based on directory
                if terminal['current_dir'] and terminal['current_dir'] != '~':
                    dir_name = Path(terminal['current_dir']).name
                    print(f"   📁 {dir_name} (from current directory)")
                
                # Show some existing projects
                print("   📂 Available projects:")
                for project in projects[:5]:
                    print(f"      {project['name']}")
                
                new_name = input(f"\n✏️  Enter new project name: ").strip()
                
                if new_name:
                    print(f"🔄 Renaming terminal {terminal_num} to '{new_name}'...")
                    if rename_terminal(terminal['id'], new_name):
                        print(f"✅ Successfully renamed to '{new_name}'")
                        
                        # Create project folder
                        project_dir = Path.home() / "Desktop" / "App_Images" / new_name / "screenshots"
                        project_dir.mkdir(parents=True, exist_ok=True)
                        print(f"📁 Created project folder: {project_dir}")
                        
                    else:
                        print("❌ Failed to rename terminal")
                    
                    input("\nPress Enter to continue...")
            else:
                print("❌ Invalid terminal number")
                input("Press Enter to continue...")
        else:
            print("❌ Invalid choice")
            input("Press Enter to continue...")
        
        print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main()