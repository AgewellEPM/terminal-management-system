#!/usr/bin/env python3
"""
🚀 TERMINAL SYSTEM MANAGER - Production-Ready Startup
Manages all terminal system components with health monitoring
"""

import os
import sys
import time
import json
import signal
import subprocess
from pathlib import Path
from datetime import datetime
import logging

class TerminalSystemManager:
    def __init__(self):
        self.home = Path.home()
        self.config_dir = self.home / ".claude"
        self.config_dir.mkdir(exist_ok=True)
        
        # Setup logging
        log_file = self.config_dir / "system_manager.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Component definitions
        self.components = {
            "option_click": {
                "script": self.home / "option_click_rename.py",
                "name": "⌥ Option+Click Rename",
                "essential": True,
                "restart_count": 0,
                "max_restarts": 3
            },
            "smart_router": {
                "script": self.home / "smart_screenshot_router.py",
                "name": "📸 Smart Screenshot Router", 
                "essential": True,
                "restart_count": 0,
                "max_restarts": 3
            },
            "auto_green_dot": {
                "script": self.home / "auto_green_dot.py",
                "name": "🟢 Auto Green Dot",
                "essential": False,
                "restart_count": 0,
                "max_restarts": 3
            },
            "hotkey_listener": {
                "script": self.home / "global_hotkey_listener.py",
                "name": "⌨️ Global Hotkeys",
                "essential": True,
                "restart_count": 0,
                "max_restarts": 3
            }
        }
        
        self.processes = {}
        self.running = True
        
        # Handle shutdown gracefully
        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)
    
    def shutdown_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info("🛑 Shutdown signal received")
        self.running = False
        self.stop_all_components()
        sys.exit(0)
    
    def start_component(self, component_name):
        """Start a system component with error handling"""
        comp = self.components[component_name]
        
        if not comp["script"].exists():
            self.logger.error(f"❌ Script not found: {comp['script']}")
            return False
        
        try:
            # Stop existing process if running
            self.stop_component(component_name)
            
            # Start new process
            process = subprocess.Popen(
                [sys.executable, str(comp["script"])],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            self.processes[component_name] = {
                "process": process,
                "start_time": datetime.now(),
                "restart_count": comp["restart_count"]
            }
            
            self.logger.info(f"✅ Started: {comp['name']} (PID: {process.pid})")
            
            # Send notification for essential components
            if comp["essential"]:
                self.send_notification(
                    "System Component Started",
                    f"{comp['name']} is now active"
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start {comp['name']}: {e}")
            return False
    
    def stop_component(self, component_name):
        """Stop a component gracefully"""
        if component_name not in self.processes:
            return True
        
        proc_info = self.processes[component_name]
        process = proc_info["process"]
        
        try:
            # Try graceful shutdown first
            process.terminate()
            
            # Wait up to 5 seconds for graceful shutdown
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                process.kill()
                process.wait()
            
            comp_name = self.components[component_name]["name"]
            self.logger.info(f"🛑 Stopped: {comp_name}")
            
            del self.processes[component_name]
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping component: {e}")
            return False
    
    def check_component_health(self, component_name):
        """Check if a component is healthy"""
        if component_name not in self.processes:
            return False
        
        process = self.processes[component_name]["process"]
        
        # Check if process is still running
        if process.poll() is not None:
            # Process has died
            comp = self.components[component_name]
            self.logger.warning(f"⚠️ Component died: {comp['name']}")
            
            # Auto-restart if under limit
            if comp["restart_count"] < comp["max_restarts"]:
                self.logger.info(f"🔄 Auto-restarting {comp['name']}")
                comp["restart_count"] += 1
                return self.start_component(component_name)
            else:
                self.logger.error(f"❌ Max restarts reached for {comp['name']}")
                if comp["essential"]:
                    self.send_notification(
                        "System Component Failed",
                        f"{comp['name']} failed to restart"
                    )
                return False
        
        return True
    
    def start_all_components(self):
        """Start all system components"""
        self.logger.info("🚀 Starting Terminal Management System")
        
        success_count = 0
        essential_count = 0
        
        for name, comp in self.components.items():
            if self.start_component(name):
                success_count += 1
                if comp["essential"]:
                    essential_count += 1
            time.sleep(1)  # Brief delay between starts
        
        total = len(self.components)
        essential_total = sum(1 for c in self.components.values() if c["essential"])
        
        self.logger.info(f"✅ Started {success_count}/{total} components")
        
        if essential_count == essential_total:
            self.send_notification(
                "🎛️ Terminal System Ready",
                f"All essential components are active"
            )
            return True
        else:
            self.send_notification(
                "⚠️ System Partially Started", 
                f"{essential_count}/{essential_total} essential components active"
            )
            return False
    
    def stop_all_components(self):
        """Stop all components"""
        self.logger.info("🛑 Stopping all components")
        
        stopped_count = 0
        for component_name in list(self.processes.keys()):
            if self.stop_component(component_name):
                stopped_count += 1
        
        if stopped_count > 0:
            self.logger.info(f"✅ Stopped {stopped_count} components")
    
    def monitor_system(self):
        """Monitor system health and auto-restart components"""
        self.logger.info("🔍 System monitoring started")
        
        while self.running:
            try:
                for component_name in list(self.processes.keys()):
                    self.check_component_health(component_name)
                
                time.sleep(10)  # Check every 10 seconds
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"❌ Monitor error: {e}")
                time.sleep(30)  # Wait before retrying
        
        self.logger.info("🔍 System monitoring stopped")
    
    def send_notification(self, title, message):
        """Send macOS notification"""
        try:
            subprocess.run([
                'osascript', '-e',
                f'display notification "{message}" with title "{title}" sound name "Glass"'
            ], check=False, timeout=5)
        except:
            pass
    
    def get_system_status(self):
        """Get detailed system status"""
        status = {
            "running_components": len(self.processes),
            "total_components": len(self.components),
            "essential_running": 0,
            "essential_total": sum(1 for c in self.components.values() if c["essential"]),
            "components": {}
        }
        
        for name, comp in self.components.items():
            is_running = name in self.processes and self.processes[name]["process"].poll() is None
            
            if is_running and comp["essential"]:
                status["essential_running"] += 1
            
            status["components"][name] = {
                "name": comp["name"],
                "running": is_running,
                "essential": comp["essential"],
                "restart_count": comp["restart_count"],
                "pid": self.processes[name]["process"].pid if is_running else None
            }
        
        return status
    
    def print_status(self):
        """Print system status"""
        status = self.get_system_status()
        
        print("🎛️ TERMINAL SYSTEM STATUS")
        print("=========================")
        print()
        print(f"📊 Components: {status['running_components']}/{status['total_components']} running")
        print(f"⚡ Essential: {status['essential_running']}/{status['essential_total']} active")
        print()
        
        for name, info in status["components"].items():
            icon = "🟢" if info["running"] else "🔴"
            essential = " ⚡" if info["essential"] else ""
            pid_info = f" (PID: {info['pid']})" if info["pid"] else ""
            restarts = f" [{info['restart_count']} restarts]" if info["restart_count"] > 0 else ""
            
            print(f"{icon} {info['name']}{essential}{pid_info}{restarts}")
        
        print()
    
    def run_daemon(self):
        """Run as system daemon"""
        self.logger.info("🎛️ Terminal System Manager starting in daemon mode")
        
        # Start all components
        if not self.start_all_components():
            self.logger.warning("⚠️ Not all essential components started")
        
        # Start health monitoring
        try:
            self.monitor_system()
        finally:
            self.stop_all_components()
            self.logger.info("👋 Terminal System Manager stopped")

def main():
    """Main function"""
    manager = TerminalSystemManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            manager.start_all_components()
        elif command == "stop":
            manager.stop_all_components()
        elif command == "status":
            manager.print_status()
        elif command == "daemon":
            manager.run_daemon()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available: start, stop, status, daemon")
    else:
        # Interactive mode
        manager.print_status()
        print("💡 Use 'daemon' mode for continuous monitoring")
        print("💡 Use 'tcc' for full control center")

if __name__ == "__main__":
    main()