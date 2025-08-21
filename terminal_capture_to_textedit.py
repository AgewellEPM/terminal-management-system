#!/usr/bin/env python3
"""
📝 TERMINAL CAPTURE TO TEXTEDIT - Command+Shift+8
Same as Command+Shift+9 but opens the OCR text directly in TextEdit
"""

import subprocess
import time
import os
from pathlib import Path
from terminal_full_capture_smart import TerminalFullCapture

class TerminalCaptureToTextEdit(TerminalFullCapture):
    def __init__(self):
        super().__init__()
        print("📝 TERMINAL CAPTURE TO TEXTEDIT")
        print("===============================")
    
    def show_window_selector_and_capture_to_textedit(self):
        """Show window selector, capture, and open text in TextEdit"""
        try:
            # Show notification
            subprocess.run([
                'osascript', '-e',
                'display notification "Click on a terminal window to capture and open in TextEdit" with title "📝 Capture to TextEdit" sound name "Glass"'
            ], check=False)
            
            # Use native screencapture with interactive window selection
            temp_file = "/tmp/selected_terminal_capture_textedit.png"
            
            print("📝 Click on the terminal window to capture for TextEdit...")
            
            # Start interactive window capture
            result = subprocess.run([
                'screencapture', 
                '-i',  # Interactive mode - shows crosshair cursor
                '-w',  # Capture window when clicked
                '-x',  # No sound
                temp_file
            ], check=False)
            
            if result.returncode == 0 and Path(temp_file).exists():
                print("✅ Window selected! Starting capture for TextEdit...")
                
                # Clean up temp file
                Path(temp_file).unlink(missing_ok=True)
                
                # Start the full capture process with TextEdit opening
                self.capture_and_open_in_textedit()
                
            else:
                print("❌ No window selected or capture cancelled")
                
        except Exception as e:
            print(f"❌ Window selector error: {e}")
    
    def capture_and_open_in_textedit(self):
        """Perform full capture and open result in TextEdit"""
        print("📸 Starting terminal capture for TextEdit...")
        
        # Run the full capture (inherited from parent class)
        captured_image_path = self.full_capture()
        
        if captured_image_path:
            # Get the text file path
            text_file_path = Path(captured_image_path).with_suffix('.txt')
            
            if text_file_path.exists():
                print(f"📝 Opening text in TextEdit: {text_file_path}")
                
                # Open the text file in TextEdit
                subprocess.run([
                    'open', '-a', 'TextEdit', str(text_file_path)
                ], check=False)
                
                # Show completion notification
                subprocess.run([
                    'osascript', '-e',
                    'display notification "Terminal text opened in TextEdit" with title "📝 TextEdit Ready" sound name "Hero"'
                ], check=False)
                
            else:
                print("❌ Text file not found, opening TextEdit with OCR...")
                self.fallback_open_ocr_in_textedit(captured_image_path)
        else:
            print("❌ Capture failed")
    
    def fallback_open_ocr_in_textedit(self, image_path):
        """Fallback: extract OCR and create new TextEdit document"""
        try:
            print("🔍 Extracting OCR for TextEdit...")
            
            # Extract text using OCR
            extracted_text = self.extract_text_with_ocr(Path(image_path))
            
            # Create temporary text file
            temp_text_file = "/tmp/terminal_capture_ocr.txt"
            
            with open(temp_text_file, 'w', encoding='utf-8') as f:
                f.write(f"Terminal Capture OCR - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                f.write(extracted_text)
            
            # Open in TextEdit
            subprocess.run([
                'open', '-a', 'TextEdit', temp_text_file
            ], check=False)
            
            print("✅ OCR text opened in TextEdit")
            
        except Exception as e:
            print(f"❌ Fallback OCR error: {e}")

def main():
    """Run terminal capture to TextEdit"""
    capturer = TerminalCaptureToTextEdit()
    capturer.show_window_selector_and_capture_to_textedit()

if __name__ == "__main__":
    main()