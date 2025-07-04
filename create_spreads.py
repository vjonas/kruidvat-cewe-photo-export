#!/usr/bin/env python3
"""
PDF Spread Creator
Converts a PDF to spread format where consecutive pages are combined side by side
"""

import os
import sys
import argparse
from PIL import Image
import fitz  # PyMuPDF
from tqdm import tqdm


class PDFSpreadCreator:
    def __init__(self, input_pdf, output_pdf=None, start_spread_page=2, dpi=300):
        self.input_pdf = input_pdf
        self.output_pdf = output_pdf or self._generate_output_name()
        self.start_spread_page = start_spread_page
        self.dpi = dpi
        
        # Create temporary directory for images
        self.temp_dir = "temp_spreads"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_pdf) if os.path.dirname(self.output_pdf) else ".", exist_ok=True)
    
    def _generate_output_name(self):
        """Generate output filename based on input"""
        base_name = os.path.splitext(os.path.basename(self.input_pdf))[0]
        return f"output/{base_name}_spreads.pdf"
    
    def extract_pages_as_images(self):
        """Extract all pages from PDF as high-quality images"""
        print("📄 Extracting pages from PDF...")
        
        doc = fitz.open(self.input_pdf)
        page_images = []
        
        for page_num in tqdm(range(len(doc)), desc="Extracting pages"):
            page = doc[page_num]
            
            # Get page as image with high DPI
            mat = fitz.Matrix(self.dpi / 72, self.dpi / 72)  # 72 is default DPI
            pix = page.get_pixmap(matrix=mat)
            
            # Save as temporary image
            temp_path = os.path.join(self.temp_dir, f"page_{page_num + 1:03d}.png")
            pix.save(temp_path)
            page_images.append(temp_path)
        
        doc.close()
        print(f"✅ Extracted {len(page_images)} pages")
        return page_images
    
    def create_spread(self, left_page_path, right_page_path, output_path):
        """Create a spread by combining two pages side by side"""
        # Open both images
        left_img = Image.open(left_page_path)
        right_img = Image.open(right_page_path)
        
        # Ensure both images are the same height
        max_height = max(left_img.height, right_img.height)
        
        # Resize if needed to match heights
        if left_img.height != max_height:
            left_img = left_img.resize((
                int(left_img.width * max_height / left_img.height),
                max_height
            ), Image.Resampling.LANCZOS)
        
        if right_img.height != max_height:
            right_img = right_img.resize((
                int(right_img.width * max_height / right_img.height),
                max_height
            ), Image.Resampling.LANCZOS)
        
        # Create new image with combined width
        spread_width = left_img.width + right_img.width
        spread_img = Image.new('RGB', (spread_width, max_height), 'white')
        
        # Paste both images
        spread_img.paste(left_img, (0, 0))
        spread_img.paste(right_img, (left_img.width, 0))
        
        # Save the spread
        spread_img.save(output_path, 'PNG', quality=95)
        
        # Clean up
        left_img.close()
        right_img.close()
        spread_img.close()
        
        return output_path
    
    def create_spreads(self):
        """Create spreads from the extracted pages"""
        print("📖 Creating spreads...")
        
        # Extract pages first
        page_images = self.extract_pages_as_images()
        
        final_pages = []
        
        # Handle pages before spread starts (individual pages)
        for i in range(min(self.start_spread_page - 1, len(page_images))):
            final_pages.append(page_images[i])
            print(f"📄 Added single page: {i + 1}")
        
        # Handle spread pages (pairs)
        spread_count = 0
        for i in range(self.start_spread_page - 1, len(page_images), 2):
            if i + 1 < len(page_images):
                # Create spread from two pages
                left_page = page_images[i]
                right_page = page_images[i + 1]
                
                spread_path = os.path.join(self.temp_dir, f"spread_{spread_count:03d}.png")
                self.create_spread(left_page, right_page, spread_path)
                final_pages.append(spread_path)
                spread_count += 1
                
                print(f"📖 Created spread: pages {i + 1}-{i + 2}")
            else:
                # Odd page at the end, add as single page
                final_pages.append(page_images[i])
                print(f"📄 Added final single page: {i + 1}")
        
        return final_pages
    
    def create_pdf_with_pymupdf(self, image_paths):
        """Create final PDF using PyMuPDF instead of img2pdf"""
        print("📚 Creating final PDF...")
        
        try:
            # Create a new PDF document
            doc = fitz.open()
            
            for i, image_path in enumerate(tqdm(image_paths, desc="Adding pages to PDF")):
                # Open image
                img = Image.open(image_path)
                
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as temporary JPEG for PyMuPDF
                temp_jpg = os.path.join(self.temp_dir, f"temp_{i}.jpg")
                img.save(temp_jpg, 'JPEG', quality=95)
                img.close()
                
                # Insert image into PDF
                img_doc = fitz.open(temp_jpg)
                pdf_bytes = img_doc.convert_to_pdf()
                img_doc.close()
                
                # Insert the page
                img_pdf = fitz.open("pdf", pdf_bytes)
                doc.insert_pdf(img_pdf)
                img_pdf.close()
                
                # Clean up temp file
                os.remove(temp_jpg)
            
            # Save the final PDF
            doc.save(self.output_pdf)
            doc.close()
            
            print(f"✅ Spread PDF created: {self.output_pdf}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating PDF: {e}")
            return False
    
    def cleanup(self):
        """Clean up temporary files"""
        print("🧹 Cleaning up temporary files...")
        
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def run(self):
        """Main execution method"""
        print("🚀 Starting PDF Spread Creator")
        print(f"📄 Input PDF: {self.input_pdf}")
        print(f"📖 Output PDF: {self.output_pdf}")
        print(f"📚 Spread starts from page: {self.start_spread_page}")
        print(f"🔍 DPI: {self.dpi}")
        print()
        
        try:
            # Create spreads
            final_pages = self.create_spreads()
            
            if not final_pages:
                print("❌ No pages to process!")
                return False
            
            # Create final PDF using PyMuPDF
            success = self.create_pdf_with_pymupdf(final_pages)
            
            if success:
                # Get file size
                file_size = os.path.getsize(self.output_pdf)
                print()
                print(f"🎉 Success! Spread PDF created!")
                print(f"📁 File size: {file_size / (1024*1024):.2f} MB")
                print(f"📚 Total pages in spread PDF: {len(final_pages)}")
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
            
        finally:
            # Always cleanup
            self.cleanup()


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to spread format")
    parser.add_argument("input_pdf", help="Input PDF file path")
    parser.add_argument("-o", "--output", help="Output PDF file path (optional)")
    parser.add_argument("-s", "--start-page", type=int, default=2, 
                        help="Page number to start spreads from (default: 2)")
    parser.add_argument("-d", "--dpi", type=int, default=300,
                        help="DPI for image extraction (default: 300)")
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_pdf):
        print(f"❌ Error: Input file '{args.input_pdf}' not found!")
        sys.exit(1)
    
    # Create spread creator
    creator = PDFSpreadCreator(
        input_pdf=args.input_pdf,
        output_pdf=args.output,
        start_spread_page=args.start_page,
        dpi=args.dpi
    )
    
    # Run the conversion
    success = creator.run()
    
    if success:
        print("\n🎉 PDF spread creation completed successfully!")
    else:
        print("\n😞 PDF spread creation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main() 