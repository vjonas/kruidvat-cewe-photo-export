# Enhanced CEWE Photo Book Fetcher

This project provides multiple ways to download images from CEWE photo books and create PDFs, including an enhanced web interface with automatic URL scraping.

## 🆕 New Features

- **🌐 CEWE URL Fetcher**: Automatically extract image URLs from CEWE photo book pages
- **📱 Enhanced Web Interface**: User-friendly web UI for all operations
- **🔍 Auto Page Detection**: Automatically detect the total number of pages
- **📐 Configurable Quality**: Adjustable image width (default: 1080px)
- **📖 Spread Creation**: Convert PDFs to 2-page spread format

## Features

- Fetches images from CEWE photo book URLs with automatic URL pattern extraction
- Handles network errors gracefully with retry logic
- Shows progress bar during download
- Creates high-quality PDF from downloaded images
- Respects server limits with small delays between requests
- **NEW**: Convert PDF to spread format (2 pages side by side)
- **NEW**: Web interface for easy operation

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

Or use the automated setup:
```bash
./start_enhanced_web.sh
```

## Usage

### 🌐 Web Interface (Recommended)

Start the enhanced web interface:
```bash
./start_enhanced_web.sh
```

Then open your browser to: http://localhost:4200

#### CEWE URL Fetcher
1. Enter your CEWE photo book URL (e.g., `https://www.cewe-fotobuch.de/view/b5cfcec0834b21d1ea0843e55f8db21a`)
2. Configure page range (optional - auto-detects by default)
3. Set image width (default: 1080px)
4. Click "Fetch Photo Book"

The system will:
- Scrape the CEWE page to find the image URL pattern
- Extract the image source link from the page HTML
- Scale the image width from the default 80px to your specified resolution
- Download all pages and create a PDF

### 📟 Command Line Interface

#### Enhanced CEWE Fetcher
```bash
# Basic usage with CEWE URL
python3 cewe_fetcher.py "https://www.cewe-fotobuch.de/view/b5cfcec0834b21d1ea0843e55f8db21a"

# Custom page range and image width
python3 cewe_fetcher.py "https://www.cewe-fotobuch.de/view/..." -s 1 -e 50 -w 1080

# High quality images
python3 cewe_fetcher.py "https://www.cewe-fotobuch.de/view/..." -w 1600
```

#### Legacy Photo Book Fetcher
```bash
# Fetch all pages (1-98) and create PDF
python fetch_photobook.py

# Fetch specific page range
python fetch_photobook.py 1 50    # Fetch pages 1-50
python fetch_photobook.py 10 20   # Fetch pages 10-20
```

#### Create Spreads from PDF
```bash
# Basic usage - spreads start from page 2
python create_spreads.py output/photobook.pdf

# Custom spread start page
python create_spreads.py output/photobook.pdf -s 3

# Custom output file with high quality
python create_spreads.py output/photobook.pdf -o output/spreads.pdf -d 600
```

## How It Works

### CEWE URL Fetcher
1. **URL Analysis**: Takes a CEWE photo book URL and scrapes the page
2. **Pattern Extraction**: Finds the `<link rel="image_src" href="...">` element within `<div id="ips_content_wrapper" class="myAccount">`
3. **URL Scaling**: Changes the width parameter from 80px to your specified resolution (default: 1080px)
4. **Page Detection**: Automatically detects the total number of pages
5. **Download**: Fetches all pages with the discovered URL pattern
6. **PDF Creation**: Uses PyMuPDF to create a high-quality PDF

### Legacy Photo Book Fetcher
1. **URL Construction**: Takes a base CEWE URL and modifies the `page` parameter for each page
2. **Image Fetching**: Downloads each page as an image with proper error handling
3. **PDF Creation**: Uses PyMuPDF to combine all images into a single PDF file
4. **Progress Tracking**: Shows real-time progress and statistics

### Spread Creator
1. **PDF Extraction**: Extracts all pages from the input PDF as high-quality images
2. **Spread Logic**: Combines consecutive pages side by side starting from specified page
3. **Image Processing**: Ensures proper alignment and sizing of spreads
4. **PDF Generation**: Creates a new PDF with the spread layout

## Output

The system creates:
- `images/` directory with individual page images
- `output/` directory with the final PDFs
- `output/cewe_photobook_XXXXX.pdf` - the fetched photo book (CEWE fetcher)
- `output/oma_jeanne_photobook.pdf` - the combined PDF (legacy fetcher)
- `output/photobook_spreads.pdf` - the spread version (if created)

## Spread Format Example

For a photo book with pages 1-6, starting spreads from page 2:
- **Original**: Page 1 | Page 2 | Page 3 | Page 4 | Page 5 | Page 6
- **Spread**: Page 1 | [Page 2-3] | [Page 4-5] | Page 6

## Error Handling

- Network timeouts and connection errors
- Invalid image formats
- Missing pages (continues with available pages)
- Server errors (logs and continues)
- PDF processing errors
- HTML parsing errors for CEWE URLs

## Technical Details

- Uses `requests` for HTTP requests with proper headers
- Uses `BeautifulSoup4` for HTML parsing of CEWE photo book pages
- Converts images to RGB format for PDF compatibility
- Maintains original image quality
- Sorts pages numerically for correct order
- Adds small delays between requests to be respectful to the server
- Uses PyMuPDF for PDF processing and high-quality image extraction
- Web interface built with Flask and Socket.IO for real-time updates

## Command Line Options

### cewe_fetcher.py
```bash
python3 cewe_fetcher.py photobook_url [-s start_page] [-e end_page] [-w width] [-o output]
```

Options:
- `photobook_url`: CEWE photo book URL (required)
- `-s, --start-page`: Start page number (default: 1)
- `-e, --end-page`: End page number (default: auto-detect)
- `-w, --width`: Image width in pixels (default: 1080)
- `-o, --output`: Output filename (default: auto-generated)

### fetch_photobook.py
```bash
python fetch_photobook.py [start_page] [end_page]
```

### create_spreads.py
```bash
python create_spreads.py input_pdf [-o output_pdf] [-s start_page] [-d dpi]
```

Options:
- `-o, --output`: Output PDF file path (optional)
- `-s, --start-page`: Page number to start spreads from (default: 2)
- `-d, --dpi`: DPI for image extraction (default: 300)

## Web Interface Features

- **Real-time Progress**: Live updates via WebSocket
- **File Management**: List and download generated PDFs
- **Error Handling**: Clear error messages and status indicators
- **Responsive Design**: Works on desktop and mobile devices
- **Multiple Scripts**: Run different tools simultaneously

## Dependencies

- `requests>=2.28.0` - HTTP requests
- `Pillow>=10.0.0` - Image processing
- `tqdm>=4.64.0` - Progress bars
- `PyMuPDF>=1.23.0` - PDF processing
- `beautifulsoup4>=4.12.0` - HTML parsing
- `Flask>=2.3.0` - Web interface
- `Flask-SocketIO>=5.3.0` - Real-time updates

## Notes

- The CEWE URL fetcher is designed to work with CEWE photo book view URLs
- Images are saved locally and can be reused if the script is run again
- The PDF creation preserves the original image quality
- Failed page downloads are reported but don't stop the process
- Spread creation processes PDFs at high resolution for quality preservation
- Temporary files are automatically cleaned up after processing
- The web interface provides the most user-friendly experience

## Example CEWE URLs

The fetcher works with URLs like:
- `https://www.cewe-fotobuch.de/view/b5cfcec0834b21d1ea0843e55f8db21a`
- `https://cewe.kruidvat.nl/web/...` (extracted automatically from the first type)

## Troubleshooting

1. **Missing dependencies**: Run `pip install -r requirements.txt`
2. **CEWE fetcher not available**: Install `beautifulsoup4`
3. **PyMuPDF issues**: Install with `pip install PyMuPDF`
4. **Web interface port conflict**: The interface uses port 4200 by default 