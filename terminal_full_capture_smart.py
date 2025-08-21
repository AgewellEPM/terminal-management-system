#!/usr/bin/env python3
"""
📸 TERMINAL FULL CAPTURE - Smart Version
Command+Shift+9: Auto-scroll and capture entire terminal, combine into one image
"""

import subprocess
import time
import os
from PIL import Image, ImageChops
from pathlib import Path
import json

class TerminalFullCapture:
    def __init__(self):
        self.temp_dir = Path.home() / ".temp_terminal_captures"
        self.temp_dir.mkdir(exist_ok=True)
        self.previous_image = None
        self.ocr_cache = {}
        self.diff_threshold = 0.05  # 5% difference threshold
        
    def get_active_terminal_project(self):
        """Get project name from terminal with green dot"""
        try:
            script = '''
            tell application "Terminal"
                repeat with w in windows
                    try
                        set windowTitle to custom title of w
                        if windowTitle contains "🟢" then
                            return windowTitle
                        end if
                    on error
                    end try
                end repeat
                return "Terminal"
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=False)
            
            if result.returncode == 0 and "🟢" in result.stdout:
                title = result.stdout.strip()
                project_name = title.replace("🟢", "").split("|")[0].strip()
                return project_name if project_name else "Terminal"
            
            return "Terminal"
            
        except Exception as e:
            print(f"❌ Project detection error: {e}")
            return "Terminal"
    
    def get_terminal_window_bounds(self):
        """Get Terminal window bounds using AXUIElementCopyAttributeValue"""
        try:
            script = '''
            tell application "Terminal"
                set frontWindow to front window
                set windowBounds to bounds of frontWindow
                return windowBounds
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                # Parse bounds: {x, y, width, height}
                bounds_str = result.stdout.strip()
                return bounds_str
            
            return None
            
        except Exception as e:
            print(f"❌ Bounds detection error: {e}")
            return None
    
    def capture_terminal_section(self, section_num):
        """Capture one section using native screencapture"""
        try:
            timestamp = int(time.time() * 1000)
            filename = f"terminal_section_{section_num}_{timestamp}.png"
            filepath = self.temp_dir / filename
            
            # Get terminal window ID for precise capture
            script = '''
            tell application "Terminal"
                return id of front window
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                window_id = result.stdout.strip()
                
                # Use native screencapture with window ID
                subprocess.run([
                    'screencapture', 
                    '-l', window_id,
                    '-x',  # No sounds
                    str(filepath)
                ], check=False)
                
                return filepath if filepath.exists() else None
            
            return None
            
        except Exception as e:
            print(f"❌ Capture error: {e}")
            return None
    
    def scroll_terminal_down(self):
        """Scroll terminal down one page"""
        try:
            script = '''
            tell application "System Events"
                tell process "Terminal"
                    key code 121
                end tell
            end tell
            '''
            subprocess.run(['osascript', '-e', script], check=False)
            time.sleep(0.3)  # Wait for scroll to complete
            
        except Exception as e:
            print(f"❌ Scroll error: {e}")
    
    def go_to_terminal_top(self):
        """Go to top of terminal"""
        try:
            script = '''
            tell application "System Events"
                tell process "Terminal"
                    key code 115 using command down
                end tell
            end tell
            '''
            subprocess.run(['osascript', '-e', script], check=False)
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Go to top error: {e}")
    
    def extract_text_with_ocr(self, image_path):
        """Extract text using native Mac OCR (VisionKit via shell)"""
        try:
            # Check cache first
            if str(image_path) in self.ocr_cache:
                return self.ocr_cache[str(image_path)]
            
            # Use your existing OCR system - calling the vision server
            result = subprocess.run([
                'python3', '/Users/lukekist/simple_vision_check.py', str(image_path)
            ], capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                text = result.stdout.strip()
                self.ocr_cache[str(image_path)] = text
                return text
            
            # Fallback to basic capture info
            return f"Terminal section captured at {time.strftime('%H:%M:%S')}"
            
        except Exception as e:
            print(f"❌ OCR error: {e}")
            return "OCR failed"
    
    def images_are_different(self, img1_path, img2_path):
        """Compare two images using PIL ImageChops for diff detection"""
        try:
            if not (img1_path and img2_path and img1_path.exists() and img2_path.exists()):
                return True
            
            img1 = Image.open(img1_path)
            img2 = Image.open(img2_path)
            
            # Resize to same size if different
            if img1.size != img2.size:
                img2 = img2.resize(img1.size)
            
            # Calculate difference
            diff = ImageChops.difference(img1, img2)
            
            # Convert to grayscale and calculate histogram
            diff_gray = diff.convert('L')
            histogram = diff_gray.histogram()
            
            # Calculate percentage of changed pixels
            total_pixels = sum(histogram)
            changed_pixels = sum(histogram[1:])  # All non-zero values
            change_percentage = changed_pixels / total_pixels if total_pixels > 0 else 0
            
            return change_percentage > self.diff_threshold
            
        except Exception as e:
            print(f"❌ Image comparison error: {e}")
            return True  # Assume different on error
    
    def combine_images(self, image_files, output_path):
        """Combine multiple screenshots into one long image"""
        try:
            if not image_files:
                return False
            
            # Open all images
            images = []
            total_height = 0
            max_width = 0
            
            for img_path in image_files:
                if img_path and img_path.exists():
                    img = Image.open(img_path)
                    images.append(img)
                    total_height += img.height
                    max_width = max(max_width, img.width)
            
            if not images:
                return False
            
            # Create combined image
            combined = Image.new('RGB', (max_width, total_height))
            y_offset = 0
            
            for img in images:
                combined.paste(img, (0, y_offset))
                y_offset += img.height
            
            # Save combined image
            combined.save(output_path)
            
            # Clean up temp files
            for img_path in image_files:
                if img_path and img_path.exists():
                    img_path.unlink()
            
            return True
            
        except Exception as e:
            print(f"❌ Combine error: {e}")
            return False
    
    def full_capture(self):
        """Perform full terminal capture"""
        print("📸 Starting terminal full capture...")
        
        # Show notification
        subprocess.run([
            'osascript', '-e',
            'display notification "Starting full terminal capture..." with title "📸 Terminal Capture" sound name "Glass"'
        ], check=False)
        
        # Go to top first
        self.go_to_terminal_top()
        
        # Capture sections with diff detection
        captured_files = []
        section = 0
        max_sections = 50  # Safety limit
        duplicate_count = 0
        max_duplicates = 3  # Stop if we see 3 identical sections
        
        while section < max_sections:
            # Capture current view
            filepath = self.capture_terminal_section(section)
            
            if filepath:
                # Check if this section is different from previous
                if self.previous_image and self.images_are_different(self.previous_image, filepath):
                    captured_files.append(filepath)
                    print(f"📸 Section {section + 1}: New content detected")
                    duplicate_count = 0  # Reset duplicate counter
                elif not self.previous_image:
                    # First capture
                    captured_files.append(filepath)
                    print(f"📸 Section {section + 1}: First section captured")
                else:
                    # Duplicate detected
                    duplicate_count += 1
                    print(f"⚫ Section {section + 1}: Duplicate content (skip {duplicate_count}/3)")
                    filepath.unlink()  # Delete duplicate
                    
                    # Break if too many duplicates (reached end)
                    if duplicate_count >= max_duplicates:
                        print("🏁 Reached end of terminal content")
                        break
                
                self.previous_image = filepath if filepath in captured_files else self.previous_image
            
            # Scroll down
            self.scroll_terminal_down()
            section += 1
        
        # Get project name and create output path
        project_name = self.get_active_terminal_project()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_filename = f"Terminal_Full_Capture_{project_name}_{timestamp}.png"
        
        # Route to project folder
        project_dir = Path.home() / "Desktop" / "App_Images" / project_name / "screenshots"
        project_dir.mkdir(parents=True, exist_ok=True)
        output_path = project_dir / output_filename
        
        # Combine images
        if self.combine_images(captured_files, output_path):
            print(f"✅ Full terminal capture saved: {output_path}")
            
            # Extract text from final combined image using OCR
            print("🔍 Extracting text with OCR...")
            extracted_text = self.extract_text_with_ocr(output_path)
            
            # Save extracted text alongside image
            text_output_path = output_path.with_suffix('.txt')
            try:
                with open(text_output_path, 'w', encoding='utf-8') as f:
                    f.write(f"Terminal Full Capture - {project_name}\n")
                    f.write(f"Captured: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(extracted_text)
                
                print(f"📝 Text extracted and saved: {text_output_path}")
            except Exception as e:
                print(f"❌ Text save error: {e}")
            
            # Save capture metadata
            metadata = {
                "project": project_name,
                "timestamp": timestamp,
                "sections_captured": len(captured_files),
                "image_path": str(output_path),
                "text_path": str(text_output_path),
                "ocr_method": "VisionKit via simple_vision_check.py"
            }
            
            metadata_path = output_path.with_suffix('.json')
            try:
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                print(f"📊 Metadata saved: {metadata_path}")
            except Exception as e:
                print(f"❌ Metadata save error: {e}")
            
            # Show completion notification
            subprocess.run([
                'osascript', '-e',
                f'display notification "Terminal captured with OCR to {project_name}" with title "📸 Smart Capture Complete" sound name "Hero"'
            ], check=False)
            
            return str(output_path)
        else:
            print("❌ Failed to combine images")
            return None

def main():
    """Run terminal full capture"""
    capturer = TerminalFullCapture()
    capturer.full_capture()

if __name__ == "__main__":
    main()