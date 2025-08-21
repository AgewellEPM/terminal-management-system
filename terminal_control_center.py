#!/usr/bin/env python3
"""
🎛️ TERMINAL CONTROL CENTER - Master System Manager
Unified control for all terminal management features
"""

import os
import sys
import subprocess
import json
import time
import signal
from pathlib import Path
from datetime import datetime

class TerminalControlCenter:
    def __init__(self):
        self.home = Path.home()
        self.config_dir = self.home / ".claude"
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "terminal_control.json"
        self.pid_file = self.config_dir / "system_pids.json"
        
        # System components
        self.components = {
            "auto_green_dot": {
                "script": "auto_green_dot.py",
                "name": "🟢 Auto Green Dot",
                "description": "Green indicator follows terminal focus",
                "pid": None
            },
            "smart_router": {
                "script": "smart_screenshot_router.py", 
                "name": "📸 Smart Screenshot Router",
                "description": "Routes screenshots to active project folders",
                "pid": None
            },
            "option_click": {
                "script": "option_click_rename.py",
                "name": "⌥ Option+Click Rename",
                "description": "Option+click terminals to rename",
                "pid": None
            },
            "hotkey_listener": {
                "script": "global_hotkey_listener.py",
                "name": "⌨️ Global Hotkeys",
                "description": "Cmd+Shift+8/9 terminal capture",
                "pid": None
            }
        }
        
        self.load_config()
    
    def load_config(self):
        """Load system configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config
        except:
            pass
        
        # Default config
        return {
            "auto_start": True,
            "notifications": True,
            "debug_mode": False,
            "screenshot_folder": "Terminal"
        }
    
    def save_config(self, config):
        """Save system configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Config save error: {e}")
            return False
    
    def load_pids(self):
        """Load saved process IDs"""
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pids = json.load(f)
                    for component, pid in pids.items():
                        if component in self.components:
                            self.components[component]["pid"] = pid
        except:
            pass
    
    def save_pids(self):
        """Save process IDs"""
        try:
            pids = {name: comp["pid"] for name, comp in self.components.items() if comp["pid"]}
            with open(self.pid_file, 'w') as f:
                json.dump(pids, f, indent=2)
        except:
            pass
    
    def is_process_running(self, pid):
        """Check if a process is still running"""
        if not pid:
            return False
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    
    def start_component(self, component_name):
        """Start a system component"""
        if component_name not in self.components:
            return False
        
        comp = self.components[component_name]
        script_path = self.home / comp["script"]
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return False
        
        # Kill existing process if running
        self.stop_component(component_name)
        
        try:
            # Start process in background
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            comp["pid"] = process.pid
            self.save_pids()
            
            print(f"✅ Started: {comp['name']} (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {comp['name']}: {e}")
            return False
    
    def stop_component(self, component_name):
        """Stop a system component"""
        if component_name not in self.components:
            return False
        
        comp = self.components[component_name]
        
        if comp["pid"] and self.is_process_running(comp["pid"]):
            try:
                os.kill(comp["pid"], signal.SIGTERM)
                time.sleep(0.5)
                
                if self.is_process_running(comp["pid"]):
                    os.kill(comp["pid"], signal.SIGKILL)
                
                print(f"🛑 Stopped: {comp['name']}")
                comp["pid"] = None
                self.save_pids()
                return True
                
            except Exception as e:
                print(f"❌ Error stopping {comp['name']}: {e}")
        
        return False
    
    def get_system_status(self):
        """Get status of all components"""
        self.load_pids()
        status = {}
        
        for name, comp in self.components.items():
            is_running = comp["pid"] and self.is_process_running(comp["pid"])
            status[name] = {
                "name": comp["name"],
                "description": comp["description"],
                "running": is_running,
                "pid": comp["pid"] if is_running else None
            }
        
        return status
    
    def show_status(self):
        """Display system status"""
        print("🎛️ TERMINAL CONTROL CENTER STATUS")
        print("=================================")
        print()
        
        status = self.get_system_status()
        running_count = sum(1 for s in status.values() if s["running"])
        
        print(f"📊 System Status: {running_count}/{len(status)} components running")
        print()
        
        for name, info in status.items():
            status_icon = "🟢" if info["running"] else "🔴"
            pid_info = f" (PID: {info['pid']})" if info["pid"] else ""
            print(f"{status_icon} {info['name']}{pid_info}")
            print(f"   {info['description']}")
            print()
    
    def start_all(self):
        """Start all system components"""
        print("🚀 STARTING TERMINAL MANAGEMENT SYSTEM")
        print("======================================")
        print()
        
        success_count = 0
        for component_name in self.components.keys():
            if self.start_component(component_name):
                success_count += 1
            time.sleep(0.5)  # Brief delay between starts
        
        print()
        print(f"✅ Started {success_count}/{len(self.components)} components")
        
        if success_count > 0:
            self.show_notification(
                "Terminal System Started",
                f"{success_count} components are now active"
            )
        
        return success_count == len(self.components)
    
    def stop_all(self):
        """Stop all system components"""
        print("🛑 STOPPING TERMINAL MANAGEMENT SYSTEM")
        print("======================================")
        
        stopped_count = 0
        for component_name in self.components.keys():
            if self.stop_component(component_name):
                stopped_count += 1
        
        print(f"\n✅ Stopped {stopped_count} components")
        
        if stopped_count > 0:
            self.show_notification(
                "Terminal System Stopped",
                f"{stopped_count} components stopped"
            )
    
    def restart_all(self):
        """Restart all components"""
        print("🔄 RESTARTING TERMINAL MANAGEMENT SYSTEM")
        print("========================================")
        
        self.stop_all()
        time.sleep(1)
        self.start_all()
    
    def show_notification(self, title, message):
        """Show macOS notification"""
        try:
            subprocess.run([
                'osascript', '-e',
                f'display notification "{message}" with title "{title}" sound name "Glass"'
            ], check=False)
        except:
            pass
    
    def create_launch_agent(self):
        """Create macOS LaunchAgent for auto-start"""
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tinkybink.terminal-control</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{self.home}/terminal_control_center.py</string>
        <string>--auto-start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{self.home}/.claude/terminal_control.log</string>
    <key>StandardErrorPath</key>
    <string>{self.home}/.claude/terminal_control_error.log</string>
</dict>
</plist>'''
        
        plist_dir = self.home / "Library" / "LaunchAgents"
        plist_dir.mkdir(exist_ok=True)
        plist_file = plist_dir / "com.tinkybink.terminal-control.plist"
        
        try:
            with open(plist_file, 'w') as f:
                f.write(plist_content)
            
            print(f"✅ Created LaunchAgent: {plist_file}")
            print("💡 To enable auto-start on login:")
            print(f"   launchctl load {plist_file}")
            
            return True
        except Exception as e:
            print(f"❌ Failed to create LaunchAgent: {e}")
            return False
    
    def show_menu(self):
        """Show interactive menu"""
        while True:
            print("\n🎛️ TERMINAL CONTROL CENTER")
            print("==========================")
            print()
            print("📋 Options:")
            print("  1. 📊 Show Status")
            print("  2. 🚀 Start All")
            print("  3. 🛑 Stop All") 
            print("  4. 🔄 Restart All")
            print("  5. 🔧 Start Individual Component")
            print("  6. 🛠️ Stop Individual Component")
            print("  7. ⚙️ Create Auto-Start")
            print("  8. 📖 Show Quick Commands")
            print("  9. 🚪 Exit")
            print()
            
            try:
                choice = input("Choose option (1-9): ").strip()
                
                if choice == "1":
                    self.show_status()
                elif choice == "2":
                    self.start_all()
                elif choice == "3":
                    self.stop_all()
                elif choice == "4":
                    self.restart_all()
                elif choice == "5":
                    self.start_individual_menu()
                elif choice == "6":
                    self.stop_individual_menu()
                elif choice == "7":
                    self.create_launch_agent()
                elif choice == "8":
                    self.show_quick_commands()
                elif choice == "9":
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
    
    def start_individual_menu(self):
        """Menu for starting individual components"""
        print("\n🔧 START COMPONENT")
        print("==================")
        
        for i, (name, comp) in enumerate(self.components.items(), 1):
            status = "🟢" if comp["pid"] and self.is_process_running(comp["pid"]) else "🔴"
            print(f"  {i}. {status} {comp['name']}")
        
        try:
            choice = input("\nEnter component number: ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                component_names = list(self.components.keys())
                if 0 <= idx < len(component_names):
                    self.start_component(component_names[idx])
        except:
            print("❌ Invalid selection")
    
    def stop_individual_menu(self):
        """Menu for stopping individual components"""
        print("\n🛠️ STOP COMPONENT")
        print("=================")
        
        for i, (name, comp) in enumerate(self.components.items(), 1):
            status = "🟢" if comp["pid"] and self.is_process_running(comp["pid"]) else "🔴"
            print(f"  {i}. {status} {comp['name']}")
        
        try:
            choice = input("\nEnter component number: ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                component_names = list(self.components.keys())
                if 0 <= idx < len(component_names):
                    self.stop_component(component_names[idx])
        except:
            print("❌ Invalid selection")
    
    def show_quick_commands(self):
        """Show available quick commands"""
        print("\n📖 QUICK COMMANDS")
        print("=================")
        print()
        print("🎛️ System Control:")
        print("   tcc start     - Start all components")
        print("   tcc stop      - Stop all components")
        print("   tcc restart   - Restart all")
        print("   tcc status    - Show status")
        print()
        print("🏷️ Terminal Renaming:")
        print("   qr            - Quick rename popup")
        print("   rename 'name' - Direct rename")
        print("   tw            - Interactive rename")
        print()
        print("📁 Screenshot Management:")
        print("   set-folder    - Set screenshot folder")
        print("   capture       - Manual terminal capture")
        print()
        print("⌨️ Global Hotkeys:")
        print("   Cmd+Shift+9   - Terminal capture to file")
        print("   Cmd+Shift+8   - Terminal capture to TextEdit")
        print("   Option+Click  - Rename terminal (when system running)")

def main():
    """Main function"""
    control_center = TerminalControlCenter()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            control_center.start_all()
        elif command == "stop":
            control_center.stop_all()
        elif command == "restart":
            control_center.restart_all()
        elif command == "status":
            control_center.show_status()
        elif command == "--auto-start":
            # Auto-start mode for LaunchAgent
            control_center.start_all()
            # Keep running to monitor
            try:
                while True:
                    time.sleep(30)
                    # Check if components are still running
                    status = control_center.get_system_status()
                    for name, info in status.items():
                        if not info["running"]:
                            print(f"🔄 Restarting crashed component: {info['name']}")
                            control_center.start_component(name)
            except KeyboardInterrupt:
                control_center.stop_all()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available: start, stop, restart, status")
    else:
        control_center.show_menu()

if __name__ == "__main__":
    main()