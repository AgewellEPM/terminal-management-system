#!/usr/bin/env python3
"""
🔧 TERMINAL SYSTEM INSTALLER - Complete Setup
Installs and configures the entire terminal management system
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class TerminalSystemInstaller:
    def __init__(self):
        self.home = Path.home()
        self.config_dir = self.home / ".claude"
        self.config_dir.mkdir(exist_ok=True)
        
        print("🔧 TERMINAL SYSTEM INSTALLER")
        print("============================")
        print("Setting up production-ready terminal management...")
        print()
    
    def check_dependencies(self):
        """Check and install required dependencies"""
        print("📦 Checking dependencies...")
        
        required_modules = ["pynput", "watchdog", "Pillow"]
        missing = []
        
        for module in required_modules:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError:
                missing.append(module)
                print(f"❌ {module} - MISSING")
        
        if missing:
            print(f"\n🔧 Installing missing modules: {', '.join(missing)}")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install"
                ] + missing, check=True)
                print("✅ All dependencies installed")
            except subprocess.CalledProcessError:
                print("❌ Failed to install dependencies")
                return False
        
        return True
    
    def create_launch_agent(self):
        """Create macOS LaunchAgent for auto-start"""
        print("\n🚀 Setting up auto-start...")
        
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tinkybink.terminal-system</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{self.home}/terminal_system_manager.py</string>
        <string>daemon</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    <key>StandardOutPath</key>
    <string>{self.home}/.claude/system.log</string>
    <key>StandardErrorPath</key>
    <string>{self.home}/.claude/system_error.log</string>
    <key>ThrottleInterval</key>
    <integer>30</integer>
</dict>
</plist>'''
        
        plist_dir = self.home / "Library" / "LaunchAgents"
        plist_dir.mkdir(exist_ok=True)
        plist_file = plist_dir / "com.tinkybink.terminal-system.plist"
        
        try:
            with open(plist_file, 'w') as f:
                f.write(plist_content)
            
            print(f"✅ Created: {plist_file}")
            return plist_file
        except Exception as e:
            print(f"❌ Failed to create LaunchAgent: {e}")
            return None
    
    def setup_shell_integration(self):
        """Ensure all shell functions are properly set up"""
        print("\n🐚 Verifying shell integration...")
        
        zshrc = self.home / ".zshrc"
        
        if not zshrc.exists():
            print("❌ .zshrc not found")
            return False
        
        # Check if our functions exist
        try:
            with open(zshrc, 'r') as f:
                content = f.read()
            
            required_functions = ["tcc", "qr", "rename", "option-click"]
            missing_functions = []
            
            for func in required_functions:
                if func not in content:
                    missing_functions.append(func)
            
            if missing_functions:
                print(f"⚠️ Missing shell functions: {', '.join(missing_functions)}")
                print("💡 Run the terminal setup scripts to fix")
                return False
            else:
                print("✅ All shell functions present")
                return True
                
        except Exception as e:
            print(f"❌ Error checking .zshrc: {e}")
            return False
    
    def create_system_status_widget(self):
        """Create a menu bar status widget"""
        widget_script = f'''#!/usr/bin/env python3
import subprocess
import sys

def get_status():
    try:
        result = subprocess.run([
            sys.executable, 
            "{self.home}/terminal_system_manager.py", 
            "status"
        ], capture_output=True, text=True, timeout=5)
        
        if "essential_running" in result.stdout:
            return "🟢"
        else:
            return "🔴"
    except:
        return "❓"

if __name__ == "__main__":
    print(get_status())
'''
        
        widget_path = self.home / "terminal_status_widget.py"
        
        try:
            with open(widget_path, 'w') as f:
                f.write(widget_script)
            
            os.chmod(widget_path, 0o755)
            print(f"✅ Created status widget: {widget_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to create widget: {e}")
            return False
    
    def setup_spotlight_integration(self):
        """Create Spotlight-searchable commands"""
        print("\n🔍 Setting up Spotlight integration...")
        
        applications_dir = self.home / "Applications"
        applications_dir.mkdir(exist_ok=True)
        
        # Create Terminal Control Center app
        app_dir = applications_dir / "Terminal Control Center.app"
        contents_dir = app_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        
        try:
            # Create directory structure
            macos_dir.mkdir(parents=True, exist_ok=True)
            
            # Create Info.plist
            info_plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>terminal-control</string>
    <key>CFBundleIdentifier</key>
    <string>com.tinkybink.terminal-control</string>
    <key>CFBundleName</key>
    <string>Terminal Control Center</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
</dict>
</plist>'''
            
            with open(contents_dir / "Info.plist", 'w') as f:
                f.write(info_plist)
            
            # Create executable script
            exec_script = f'''#!/bin/bash
cd "{self.home}"
python3 terminal_control_center.py
'''
            
            exec_path = macos_dir / "terminal-control"
            with open(exec_path, 'w') as f:
                f.write(exec_script)
            
            os.chmod(exec_path, 0o755)
            
            print(f"✅ Created Spotlight app: {app_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create Spotlight integration: {e}")
            return False
    
    def run_installation(self):
        """Run complete installation"""
        print("🎯 Starting complete installation...\n")
        
        success_count = 0
        total_steps = 5
        
        # Step 1: Dependencies
        if self.check_dependencies():
            success_count += 1
        
        # Step 2: Shell integration
        if self.setup_shell_integration():
            success_count += 1
        
        # Step 3: Launch agent
        plist_file = self.create_launch_agent()
        if plist_file:
            success_count += 1
            
            # Try to load the launch agent
            try:
                subprocess.run(["launchctl", "load", str(plist_file)], check=True)
                print("✅ Auto-start enabled")
            except subprocess.CalledProcessError:
                print("⚠️ Auto-start created but not loaded (requires restart)")
        
        # Step 4: Status widget
        if self.create_system_status_widget():
            success_count += 1
        
        # Step 5: Spotlight integration
        if self.setup_spotlight_integration():
            success_count += 1
        
        print(f"\n🎉 INSTALLATION COMPLETE: {success_count}/{total_steps} steps successful")
        
        if success_count == total_steps:
            print("\n✅ SYSTEM READY!")
            print("==================")
            print("🎛️ Type 'tcc' to open Control Center")
            print("⌥ Option+Click terminals to rename them")
            print("📸 Screenshots auto-route to project folders")
            print("⌨️ Cmd+Shift+8/9 for terminal capture")
            print("🟢 Green dots follow your focus")
            print()
            print("💡 System will auto-start on login")
            
            # Start the system now
            try:
                subprocess.run([
                    sys.executable, 
                    str(self.home / "terminal_system_manager.py"),
                    "start"
                ])
                print("🚀 System started!")
            except:
                print("⚠️ Manual start needed: tcc start")
        
        else:
            print("\n⚠️ PARTIAL INSTALLATION")
            print("Some features may not work properly")
            print("Check error messages above")

def main():
    installer = TerminalSystemInstaller()
    installer.run_installation()

if __name__ == "__main__":
    main()