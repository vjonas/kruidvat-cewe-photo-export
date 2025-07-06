#!/usr/bin/env python3
"""
Enhanced CEWE Photo Book Fetcher
Scrapes CEWE photo book URLs to extract image patterns and fetches all pages
"""

import requests
import os
import time
from PIL import Image
from tqdm import tqdm
import sys
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
import re


class CEWEPhotoBookFetcher:
    def __init__(self, photobook_url, start_page=1, end_page=None, target_width=1080):
        self.photobook_url = photobook_url
        self.start_page = start_page
        self.end_page = end_page
        self.target_width = target_width
        self.base_image_url = None
        self.total_pages = None
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create directories
        self.images_dir = "images"
        self.output_dir = "output"
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def extract_image_url_pattern(self):
        """Extract the image URL pattern from the CEWE photo book page"""
        print(f"🔍 Analyzing photo book URL: {self.photobook_url}")
        
        try:
            response = self.session.get(self.photobook_url, timeout=30)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the div with id="ips_content_wrapper" and class="myAccount"
            content_wrapper = soup.find('div', {'id': 'ips_content_wrapper', 'class': 'myAccount'})
            
            if not content_wrapper:
                print("❌ Could not find the content wrapper div")
                return False
            
            # Find the link element with rel="image_src"
            image_link = content_wrapper.find('link', {'rel': 'image_src'})
            
            if not image_link or not image_link.get('href'):
                print("❌ Could not find the image source link")
                return False
            
            image_url = image_link['href']
            print(f"✅ Found image URL: {image_url}")
            
            # Replace width parameter and clean up the URL
            self.base_image_url = self.prepare_image_url(image_url)
            print(f"📐 Scaled to width {self.target_width}: {self.base_image_url}")
            
            # Try to detect total pages if not specified
            if self.end_page is None:
                self.detect_total_pages()
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching photo book page: {e}")
            return False
        except Exception as e:
            print(f"❌ Error parsing photo book page: {e}")
            return False
    
    def prepare_image_url(self, url):
        """Prepare the image URL by scaling width and cleaning parameters"""
        # Parse the URL
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Update width parameter
        query_params['width'] = [str(self.target_width)]
        
        # Remove skipSessionTimeout if present
        if 'skipSessionTimeout' in query_params:
            del query_params['skipSessionTimeout']
        
        # Rebuild the URL
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                             parsed.params, new_query, parsed.fragment))
        return new_url
    
    def detect_total_pages(self):
        """Try to detect the total number of pages by testing incrementally"""
        print("🔍 Detecting total pages...")
        
        # Start with a reasonable guess and work backwards
        test_pages = [100, 50, 25, 10, 5]
        
        for test_page in test_pages:
            if self.test_page_exists(test_page):
                # Found a page that exists, now find the exact end
                self.total_pages = self.binary_search_last_page(test_page, test_page + 50)
                break
        
        if self.total_pages is None:
            # If we can't detect, default to a reasonable number
            self.total_pages = 50
            print(f"⚠️  Could not detect total pages, defaulting to {self.total_pages}")
        else:
            print(f"📚 Detected {self.total_pages} total pages")
        
        if self.end_page is None:
            self.end_page = self.total_pages
    
    def test_page_exists(self, page_num):
        """Test if a specific page exists"""
        url = self.build_page_url(page_num)
        try:
            response = self.session.head(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def binary_search_last_page(self, min_page, max_page):
        """Use binary search to find the last existing page"""
        while min_page < max_page:
            mid = (min_page + max_page + 1) // 2
            if self.test_page_exists(mid):
                min_page = mid
            else:
                max_page = mid - 1
        return min_page
    
    def build_page_url(self, page_number):
        """Build URL for a specific page number"""
        if not self.base_image_url:
            return None
            
        parsed = urlparse(self.base_image_url)
        query_params = parse_qs(parsed.query)
        
        # Update the page parameter
        query_params['page'] = [str(page_number)]
        
        # Rebuild the URL
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                             parsed.params, new_query, parsed.fragment))
        return new_url
    
    def fetch_image(self, page_number):
        """Fetch image for a specific page"""
        url = self.build_page_url(page_number)
        if not url:
            return None
            
        image_path = os.path.join(self.images_dir, f"page_{page_number:03d}.jpg")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Check if response is actually an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                print(f"Warning: Page {page_number} returned non-image content: {content_type}")
                return None
            
            # Save the image
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            # Verify the image can be opened
            try:
                with Image.open(image_path) as img:
                    # Convert to RGB if needed (for PDF compatibility)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                        img.save(image_path, 'JPEG', quality=95)
                        
                return image_path
            except Exception as e:
                print(f"Error processing image for page {page_number}: {e}")
                if os.path.exists(image_path):
                    os.remove(image_path)
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page_number}: {e}")
            return None
    
    def fetch_all_images(self):
        """Fetch all images from start_page to end_page"""
        if not self.base_image_url:
            print("❌ No base image URL available. Did you run extract_image_url_pattern()?")
            return [], []
            
        print(f"📚 Fetching images from page {self.start_page} to {self.end_page}")
        
        successful_images = []
        failed_pages = []
        
        # Progress bar
        with tqdm(total=self.end_page - self.start_page + 1, desc="Fetching images") as pbar:
            for page_num in range(self.start_page, self.end_page + 1):
                image_path = self.fetch_image(page_num)
                
                if image_path:
                    successful_images.append(image_path)
                    pbar.set_postfix({"Success": len(successful_images), "Failed": len(failed_pages)})
                else:
                    failed_pages.append(page_num)
                    pbar.set_postfix({"Success": len(successful_images), "Failed": len(failed_pages)})
                
                pbar.update(1)
                
                # Small delay to be respectful to the server
                time.sleep(0.1)
        
        print(f"\n✅ Fetch complete!")
        print(f"Successfully fetched: {len(successful_images)} images")
        print(f"Failed pages: {len(failed_pages)}")
        
        if failed_pages:
            print(f"Failed page numbers: {failed_pages}")
        
        return successful_images, failed_pages
    
    def create_pdf_with_pymupdf(self, image_paths, output_filename="photobook.pdf"):
        """Create PDF from list of image paths using PyMuPDF"""
        if not image_paths:
            print("No images to create PDF from!")
            return None
            
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            print(f"📚 Creating PDF with {len(image_paths)} images...")
            
            # Sort image paths to ensure correct order
            image_paths.sort()
            
            # Try using PyMuPDF for PDF creation
            try:
                import fitz
                
                # Create a new PDF document
                doc = fitz.open()
                
                for i, image_path in enumerate(tqdm(image_paths, desc="Adding pages to PDF")):
                    # Open image
                    img = Image.open(image_path)
                    
                    # Convert to RGB if needed
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Save as temporary JPEG for PyMuPDF
                    temp_jpg = f"temp_{i}.jpg"
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
                doc.save(output_path)
                doc.close()
                
            except ImportError:
                # Fallback: if PyMuPDF is not available, inform user
                print("❌ PyMuPDF not available for advanced PDF creation")
                return None
            
            print(f"✅ PDF created successfully: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error creating PDF: {e}")
            return None
    
    def run(self, output_filename=None):
        """Main execution method"""
        print("🚀 Starting Enhanced CEWE Photo Book Fetcher")
        print(f"📖 Photo book URL: {self.photobook_url}")
        
        # Extract image URL pattern
        if not self.extract_image_url_pattern():
            print("❌ Failed to extract image URL pattern")
            return False
        
        print(f"📄 Pages: {self.start_page} to {self.end_page}")
        print(f"📐 Image width: {self.target_width}px")
        
        # Fetch all images
        successful_images, failed_pages = self.fetch_all_images()
        
        if not successful_images:
            print("❌ No images were successfully fetched. Cannot create PDF.")
            return False
        
        # Generate output filename if not provided
        if not output_filename:
            # Extract some identifier from the URL for filename
            url_hash = abs(hash(self.photobook_url)) % 100000
            output_filename = f"cewe_photobook_{url_hash}.pdf"
        else:
            # Sanitize filename and ensure .pdf extension
            import re
            # Remove or replace invalid characters
            output_filename = re.sub(r'[<>:"/\\|?*]', '_', output_filename)
            # Ensure .pdf extension
            if not output_filename.lower().endswith('.pdf'):
                output_filename += '.pdf'
        
        # Create PDF
        pdf_path = self.create_pdf_with_pymupdf(successful_images, output_filename)
        
        if pdf_path:
            print(f"\n🎉 Success! PDF created: {pdf_path}")
            print(f"📊 Total pages in PDF: {len(successful_images)}")
            
            # File size
            file_size = os.path.getsize(pdf_path)
            print(f"📁 File size: {file_size / (1024*1024):.2f} MB")
            
            return True
        else:
            print("\n❌ Failed to create PDF")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced CEWE Photo Book Fetcher")
    parser.add_argument("photobook_url", help="CEWE photo book URL")
    parser.add_argument("-s", "--start-page", type=int, default=1, 
                        help="Start page number (default: 1)")
    parser.add_argument("-e", "--end-page", type=int, default=None,
                        help="End page number (default: auto-detect)")
    parser.add_argument("-w", "--width", type=int, default=1080,
                        help="Image width in pixels (default: 1080)")
    parser.add_argument("-o", "--output", help="Output filename (default: auto-generated)")
    
    args = parser.parse_args()
    
    # Create fetcher and run
    fetcher = CEWEPhotoBookFetcher(
        photobook_url=args.photobook_url,
        start_page=args.start_page,
        end_page=args.end_page,
        target_width=args.width
    )
    
    success = fetcher.run(args.output)
    
    if success:
        print("\n🎉 Photo book PDF created successfully!")
    else:
        print("\n😞 Failed to create photo book PDF.")
        sys.exit(1)


if __name__ == "__main__":
    main() 