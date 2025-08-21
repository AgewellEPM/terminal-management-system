# 🎛️ Terminal Management System

**Production-ready macOS terminal management with auto-routing, smart indicators, and seamless renaming**

![macOS](https://img.shields.io/badge/macOS-Compatible-black?logo=apple)
![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Status](https://img.shields.io/badge/Status-Production_Ready-green)

## ✨ Features

### ⌥ **Option+Click Rename**
Hold Option and click on any terminal window to instantly rename it - works just like Finder!

### 🟢 **Smart Green Indicators**
Green dots automatically follow your active terminal window, providing visual project identification.

### 📸 **Intelligent Screenshot Routing**
Screenshots automatically organize into project folders based on your active terminal.

### ⌨️ **Global Hotkeys**
- **Cmd+Shift+9**: Full terminal capture with OCR to file
- **Cmd+Shift+8**: Full terminal capture with OCR to TextEdit

### 🎛️ **Unified Control Center**
Single command interface for managing all system components with health monitoring.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/terminal-management-system.git
cd terminal-management-system

# Run the installer
python3 install_terminal_system.py

# Start the system
./start_tinkybink_system.sh

# Or use the control center
tcc
```

## 📋 Commands

### System Control
```bash
tcc              # Open control center
tcc start        # Start all components
tcc stop         # Stop all components
tcc status       # Show system status
```

### Terminal Renaming
```bash
qr               # Quick rename popup
rename "name"    # Direct rename
tw               # Interactive menu
```

### Screenshot Management
```bash
set-folder       # Set routing folder
capture          # Manual capture
```

## 🔧 System Architecture

The system consists of several integrated components:

- **Terminal Control Center** - Unified management interface
- **System Manager** - Production daemon with auto-recovery
- **Option+Click Rename** - Native-feeling terminal renaming
- **Smart Screenshot Router** - Automatic file organization
- **Auto Green Dot** - Visual focus indicators
- **Global Hotkey Listener** - System-wide keyboard shortcuts

## 📦 Requirements

- macOS 10.15 or later
- Python 3.9+
- Required Python packages:
  - `pynput`
  - `watchdog`
  - `Pillow`

## 🚀 Installation

### Automatic Installation
```bash
python3 install_terminal_system.py
```

This will:
- Install required dependencies
- Set up shell integration
- Create LaunchAgent for auto-start
- Configure Spotlight integration
- Start all components

### Manual Installation
```bash
# Install dependencies
pip3 install pynput watchdog Pillow

# Add to ~/.zshrc
source shell_integration.sh

# Start components
python3 terminal_control_center.py start
```

## ⚙️ Configuration

Configuration files are stored in `~/.claude/`:
- `terminal_control.json` - System settings
- `screenshot_config.json` - Screenshot routing
- `system_pids.json` - Process management

## 🔍 Troubleshooting

### Check System Status
```bash
tcc status
```

### View Logs
```bash
tail -f ~/.claude/system_manager.log
```

### Reset System
```bash
tcc restart
```

### Common Issues

**Option+Click not working:**
- Grant Terminal accessibility permissions in System Preferences

**Screenshots not routing:**
- Verify smart router is running: `tcc status`
- Set custom folder: `set-folder`

**Hotkeys not responding:**
- Check for conflicts in System Preferences → Keyboard → Shortcuts

## 📊 Performance

- **Memory**: ~50MB total
- **CPU**: <1% during normal operation
- **Auto-recovery**: Components restart automatically (up to 3 times)
- **Health monitoring**: Every 10 seconds

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built with [Claude Code](https://claude.ai/code) - Advanced terminal workspace management for power users

---

**🎛️ Transform your terminal workflow with intelligent automation!**