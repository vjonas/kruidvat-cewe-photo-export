# CEWE Photo Book Fetcher

This project fetches images from CEWE photo book pages and combines them into a single PDF file.

## Features

- Fetches images from specified page range (default: pages 1-98)
- Handles network errors gracefully with retry logic
- Shows progress bar during download
- Creates high-quality PDF from downloaded images
- Respects server limits with small delays between requests

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

## Output

The script creates:
- `images/` directory with individual page images
- `output/` directory with the final PDF
- `output/oma_jeanne_photobook.pdf` - the combined PDF file

## How it Works

1. **URL Construction**: Takes the base CEWE URL and modifies the `page` parameter for each page
2. **Image Fetching**: Downloads each page as an image with proper error handling
3. **PDF Creation**: Uses `img2pdf` to combine all images into a single PDF file
4. **Progress Tracking**: Shows real-time progress and statistics

## Error Handling

- Network timeouts and connection errors
- Invalid image formats
- Missing pages (continues with available pages)
- Server errors (logs and continues)

## Technical Details

- Uses `requests` for HTTP requests with proper headers
- Converts images to RGB format for PDF compatibility
- Maintains original image quality
- Sorts pages numerically for correct order
- Adds small delays between requests to be respectful to the server

## Notes

- The script is designed to work with the specific CEWE photo book URL format
- Images are saved locally and can be reused if the script is run again
- The PDF creation preserves the original image quality
- Failed page downloads are reported but don't stop the process 