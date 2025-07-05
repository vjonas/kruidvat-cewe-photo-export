# CEWE Photo Book Fetcher

This project fetches images from CEWE photo book pages and combines them into a single PDF file.

## Features

- Fetches images from specified page range (default: pages 1-98)
- Handles network errors gracefully with retry logic
- Shows progress bar during download
- Creates high-quality PDF from downloaded images
- Respects server limits with small delays between requests
- **NEW**: Convert PDF to spread format (2 pages side by side)

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
Fetch all pages (1-98) and create PDF:
```bash
python fetch_photobook.py
```

### Custom Page Range
Fetch specific page range:
```bash
python fetch_photobook.py 1 50    # Fetch pages 1-50
python fetch_photobook.py 10 20   # Fetch pages 10-20
```

### Create Spreads from PDF
Convert your generated PDF to spread format (2 pages side by side):
```bash
# Basic usage - spreads start from page 2
python create_spreads.py output/oma_jeanne_photobook.pdf

# Custom spread start page
python create_spreads.py output/oma_jeanne_photobook.pdf -s 3

# Custom output file
python create_spreads.py output/oma_jeanne_photobook.pdf -o output/my_spreads.pdf

# High DPI for better quality
python create_spreads.py output/oma_jeanne_photobook.pdf -d 600
```

## Output

The script creates:
- `images/` directory with individual page images
- `output/` directory with the final PDF
- `output/oma_jeanne_photobook.pdf` - the combined PDF file
- `output/oma_jeanne_photobook_spreads.pdf` - the spread version (if created)

## How it Works

### Photo Book Fetcher
1. **URL Construction**: Takes the base CEWE URL and modifies the `page` parameter for each page
2. **Image Fetching**: Downloads each page as an image with proper error handling
3. **PDF Creation**: Uses `img2pdf` to combine all images into a single PDF file
4. **Progress Tracking**: Shows real-time progress and statistics

### Spread Creator
1. **PDF Extraction**: Extracts all pages from the input PDF as high-quality images
2. **Spread Logic**: Combines consecutive pages side by side starting from specified page
3. **Image Processing**: Ensures proper alignment and sizing of spreads
4. **PDF Generation**: Creates a new PDF with the spread layout

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

## Technical Details

- Uses `requests` for HTTP requests with proper headers
- Converts images to RGB format for PDF compatibility
- Maintains original image quality
- Sorts pages numerically for correct order
- Adds small delays between requests to be respectful to the server
- Uses PyMuPDF for PDF processing and high-quality image extraction

## Command Line Options

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

## Web Interface

**NEW**: A web interface is now available to run the scripts easily!

### Starting the Web Interface
```bash
./start_web_interface.sh
```

Then open your browser to: `http://localhost:5000`

### Features
- **Modern Web UI**: Clean, responsive interface that works on desktop and mobile
- **Real-time Output**: See script output in real-time as it runs
- **Script Management**: Start, stop, and monitor both photo book fetcher and spreads creator
- **File Downloads**: Download generated PDFs directly from the web interface  
- **Progress Indicators**: Visual status indicators and progress tracking
- **Mobile Friendly**: Responsive design that works on all devices

### Web Interface Usage
1. **Photo Book Fetcher**: Click "Run Photo Book Fetcher" to download all pages (1-98)
2. **Spreads Creator**: Click "Create Spreads" to convert your PDF to spread format
3. **View Output**: Click "Show Output" to see real-time script output
4. **Download Files**: Use the "Generated Files" section to download your PDFs
5. **Stop Scripts**: Use the "Stop" button to cancel running scripts

The web interface handles all the interactive prompts automatically and provides a much more user-friendly experience than the command line.

## Notes

- The script is designed to work with the specific CEWE photo book URL format
- Images are saved locally and can be reused if the script is run again
- The PDF creation preserves the original image quality
- Failed page downloads are reported but don't stop the process
- Spread creation processes PDFs at high resolution for quality preservation
- Temporary files are automatically cleaned up after processing 