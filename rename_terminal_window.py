#!/usr/bin/env python3
"""
🏷️ RENAME TERMINAL WINDOW - Set custom window titles
Multiple ways to rename terminal windows at the top
"""

import subprocess
import sys

def rename_current_window(new_title):
    """Rename the current terminal window"""
    try:
        script = f'''
        tell application "Terminal"
            set custom title of front window to "{new_title}"
            set title displays custom title of front window to true
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print(f"✅ Terminal window renamed to: {new_title}")
            
            # Show notification
            subprocess.run([
                'osascript', '-e',
                f'display notification "Window renamed to {new_title}" with title "🏷️ Terminal Renamed" sound name "Glass"'
            ], check=False)
            
            return True
        else:
            print(f"❌ Failed to rename window: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Rename error: {e}")
        return False

def show_all_windows():
    """Show all terminal windows and their current titles"""
    try:
        script = '''
        tell application "Terminal"
            set windowList to {}
            repeat with i from 1 to count of windows
                try
                    set windowInfo to (i as string) & ": " & (name of window i)
                    set end of windowList to windowInfo
                on error
                    set end of windowList to (i as string) & ": (Unnamed)"
                end try
            end repeat
            return windowList
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            windows_output = result.stdout.strip()
            if windows_output and windows_output != "{}":
                print("🖥️ CURRENT TERMINAL WINDOWS:")
                print("============================")
                
                # Parse AppleScript list format
                windows_output = windows_output.replace("{", "").replace("}", "")
                if windows_output:
                    windows = [w.strip().strip('"') for w in windows_output.split('", "') if w.strip()]
                    for window in windows:
                        print(f"   {window}")
                else:
                    print("   No windows found")
            else:
                print("🖥️ No terminal windows found")
        
    except Exception as e:
        print(f"❌ Window list error: {e}")

def interactive_rename():
    """Interactive window renaming"""
    print("🏷️ TERMINAL WINDOW RENAMER")
    print("==========================")
    
    # Show current windows
    show_all_windows()
    print()
    
    # Get current window title
    try:
        current_title = subprocess.run([
            'osascript', '-e', 
            'tell application "Terminal" to return name of front window'
        ], capture_output=True, text=True, check=False).stdout.strip()
        
        print(f"🎯 Current window: {current_title}")
    except:
        print("🎯 Current window: Unknown")
    
    print()
    print("💡 Enter new window title (or press Enter to cancel):")
    
    try:
        new_title = input("🏷️ New title: ").strip()
        
        if new_title:
            return rename_current_window(new_title)
        else:
            print("❌ Cancelled")
            return False
            
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
        return False

def create_shell_functions():
    """Create shell functions for easy terminal renaming"""
    shell_functions = '''
# Terminal Window Renaming Functions
# Add these to your ~/.zshrc file

# Rename current terminal window
rename() {
    if [ -z "$1" ]; then
        echo "Usage: rename <new_title>"
        echo "Example: rename 'My Project'"
        return 1
    fi
    
    osascript -e "tell application \\"Terminal\\" to set custom title of front window to \\"$1\\""
    osascript -e "tell application \\"Terminal\\" to set title displays custom title of front window to true"
    echo "✅ Terminal renamed to: $1"
}

# Reset terminal title to default
reset-title() {
    osascript -e "tell application \\"Terminal\\" to set title displays custom title of front window to false"
    echo "✅ Terminal title reset to default"
}

# Show all terminal windows
show-windows() {
    osascript -e 'tell application "Terminal"
        repeat with i from 1 to count of windows
            try
                log (i as string) & ": " & (name of window i)
            on error
                log (i as string) & ": (Unnamed)"
            end try
        end repeat
    end tell' 2>&1 | grep -v "Tell"
}
'''
    
    return shell_functions

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Command line usage
        new_title = " ".join(sys.argv[1:])
        rename_current_window(new_title)
    else:
        # Interactive mode
        print("🏷️ TERMINAL WINDOW MANAGEMENT")
        print("=============================")
        print()
        print("📋 Options:")
        print("1. Rename current window")
        print("2. Show all windows")
        print("3. Show shell functions")
        print("4. Quit")
        print()
        
        try:
            choice = input("Choose option (1-4): ").strip()
            
            if choice == "1":
                interactive_rename()
            elif choice == "2":
                show_all_windows()
            elif choice == "3":
                print("🔧 SHELL FUNCTIONS:")
                print("===================")
                print(create_shell_functions())
                print()
                print("💡 Add these to your ~/.zshrc file for easy terminal renaming!")
            elif choice == "4":
                print("👋 Goodbye!")
            else:
                print("❌ Invalid choice")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()