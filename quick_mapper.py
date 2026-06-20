#!/usr/bin/env python3
"""Quick terminal mapper"""

import subprocess
from pathlib import Path

def get_terminals():
    """Get terminal info"""
    script = '''
    tell application "Terminal"
        set terminalInfo to ""
        repeat with w in windows
            set windowId to id of w
            try
                set customTitle to custom title of w
            on error
                set customTitle to ""
            end try
            set terminalInfo to terminalInfo & windowId & "|" & customTitle & "\n"
        end repeat
        return terminalInfo
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    terminals = []
    
    if result.stdout:
        for line in result.stdout.strip().split('\n'):
            if line and '|' in line:
                parts = line.split('|')
                window_id = parts[0]
                custom_title = parts[1] if len(parts) > 1 else ""
                
                # Clean title
                display_title = custom_title
                if display_title.startswith("🟢 "):
                    display_title = display_title[3:]
                elif display_title.startswith("⚫ "):
                    display_title = display_title[3:]
                
                is_active = "🟢" in custom_title
                terminals.append({
                    'id': window_id,
                    'title': display_title or f"Terminal-{window_id}",
                    'is_active': is_active
                })
    
    return terminals

def rename_terminal(window_id, new_name):
    """Rename terminal"""
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

# Get current terminals
terminals = get_terminals()

print("🖥️ CURRENT TERMINALS TO MAP:")
print("=" * 50)

for i, terminal in enumerate(terminals, 1):
    status = "🟢 ACTIVE" if terminal['is_active'] else "⚫ inactive"
    print(f"{i}. {status} │ {terminal['title']} (ID: {terminal['id']})")

print("\n📁 EXISTING PROJECT FOLDERS:")
app_images = Path.home() / "Desktop" / "App_Images"
if app_images.exists():
    for folder in sorted(app_images.iterdir()):
        if folder.is_dir():
            print(f"   📂 {folder.name}")

print(f"\n📋 You have {len(terminals)} terminals to map")
print("💡 SUGGESTIONS FOR MAPPING:")
print("   🎯 TinkyBinkAAC - for the main AAC project")
print("   🔧 TerminalSystem - for this terminal management system") 
print("   🦀 TinkyRust - for the Rust backend")
print("   🌐 WebInterface - for web development")
print("   📊 Analytics - for data analysis")
print("   🧪 Testing - for testing and experiments")

print(f"\n🔧 TO RENAME TERMINALS:")
print("Use the master system menu bar (🐷) -> Terminal Mapping")
print("Or run individual rename commands:")

for i, terminal in enumerate(terminals, 1):
    print(f"   Terminal {i}: python3 -c \"import subprocess; subprocess.run(['osascript', '-e', 'tell application \\\"Terminal\\\" to set custom title of window id {terminal['id']} to \\\"PROJECT_NAME\\\"'])\"")

print(f"\n✅ After renaming, screenshots will route to:")
print("   ~/Desktop/App_Images/[PROJECT_NAME]/screenshots/")

# Show which terminal is currently active for immediate testing
active_terminal = next((t for t in terminals if t['is_active']), None)
if active_terminal:
    print(f"\n🎯 CURRENTLY ACTIVE: {active_terminal['title']}")
    print("   Screenshots will route here until you map to a project name")