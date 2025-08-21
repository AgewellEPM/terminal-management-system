#!/bin/bash
# 🚀 TINKYBINK Terminal System - Quick Start

echo "🎛️ TINKYBINK TERMINAL SYSTEM"
echo "============================"
echo ""
echo "🚀 Starting complete terminal management system..."
echo ""

# Kill any existing instances
echo "🧹 Cleaning up existing processes..."
pkill -f "option_click_rename.py" 2>/dev/null
pkill -f "smart_screenshot_router.py" 2>/dev/null  
pkill -f "auto_green_dot.py" 2>/dev/null
pkill -f "global_hotkey_listener.py" 2>/dev/null

sleep 2

# Start the system manager  
echo "🎯 Starting system manager..."
python3 /Users/lukekist/terminal_system_manager.py start

echo ""
echo "✅ TINKYBINK SYSTEM READY!"
echo "========================="
echo ""
echo "🎛️ Control Center: tcc"
echo "⌥ Option+Click: Rename any terminal"
echo "📸 Screenshots: Auto-route to projects" 
echo "⌨️ Hotkeys: Cmd+Shift+8/9 for capture"
echo "🟢 Green dots: Follow your focus"
echo ""
echo "📖 Full guide: cat TERMINAL_SYSTEM_GUIDE.md"