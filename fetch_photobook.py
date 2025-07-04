#!/usr/bin/env python3
"""
CEWE Photo Book Fetcher
Fetches images from CEWE photo book pages and combines them into a PDF
"""

import requests
import os
import time
from PIL import Image
import img2pdf
from tqdm import tqdm
import sys
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


class PhotoBookFetcher:
    def __init__(self, base_url, start_page=1, end_page=98):
        self.base_url = base_url
        self.start_page = start_page
        self.end_page = end_page
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create directories
        self.images_dir = "images"
        self.output_dir = "output"
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def build_page_url(self, page_number):
        """Build URL for a specific page number"""
        parsed = urlparse(self.base_url)
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
        print(f"Fetching images from page {self.start_page} to {self.end_page}")
        
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
        
        print(f"\nFetch complete!")
        print(f"Successfully fetched: {len(successful_images)} images")
        print(f"Failed pages: {len(failed_pages)}")
        
        if failed_pages:
            print(f"Failed page numbers: {failed_pages}")
        
        return successful_images, failed_pages
    
    def create_pdf(self, image_paths, output_filename="photobook.pdf"):
        """Create PDF from list of image paths"""
        if not image_paths:
            print("No images to create PDF from!")
            return None
            
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            print(f"Creating PDF with {len(image_paths)} images...")
            
            # Sort image paths to ensure correct order
            image_paths.sort()
            
            # Create PDF
            with open(output_path, "wb") as pdf_file:
                pdf_file.write(img2pdf.convert(image_paths))
            
            print(f"PDF created successfully: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error creating PDF: {e}")
            return None
    
    def run(self, output_filename="photobook.pdf"):
        """Main execution method"""
        print("Starting CEWE Photo Book Fetcher")
        print(f"Base URL: {self.base_url}")
        print(f"Pages: {self.start_page} to {self.end_page}")
        
        # Fetch all images
        successful_images, failed_pages = self.fetch_all_images()
        
        if not successful_images:
            print("No images were successfully fetched. Cannot create PDF.")
            return False
        
        # Create PDF
        pdf_path = self.create_pdf(successful_images, output_filename)
        
        if pdf_path:
            print(f"\n✅ Success! PDF created: {pdf_path}")
            print(f"📊 Total pages in PDF: {len(successful_images)}")
            
            # File size
            file_size = os.path.getsize(pdf_path)
            print(f"📁 File size: {file_size / (1024*1024):.2f} MB")
            
            return True
        else:
            print("\n❌ Failed to create PDF")
            return False


def main():
    # The base URL from the user
    base_url = "https://cewe.kruidvat.nl/web/50000005/photoBookPageRender.do?orderId=841684379&position=0&page=98&width=1080&hash=d19a90283ed4fd02254ff7710711be30&access=PY4EZ5"
    
    # Allow command line arguments for page range
    start_page = 1
    end_page = 98
    
    if len(sys.argv) > 1:
        try:
            start_page = int(sys.argv[1])
            if len(sys.argv) > 2:
                end_page = int(sys.argv[2])
        except ValueError:
            print("Invalid page numbers. Using default range 1-98.")
    
    # Create fetcher and run
    fetcher = PhotoBookFetcher(base_url, start_page, end_page)
    success = fetcher.run("oma_jeanne_photobook.pdf")
    
    if success:
        print("\n🎉 Photo book PDF created successfully!")
    else:
        print("\n😞 Failed to create photo book PDF.")
        sys.exit(1)


if __name__ == "__main__":
    main() 