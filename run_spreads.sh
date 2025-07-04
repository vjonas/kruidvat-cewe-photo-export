#!/bin/bash

# Run the spreads creation script
echo "🚀 Creating spreads from your photo book PDF..."
echo "📄 Input: ./output/oma_jeanne_photobook_final.pdf"
echo "📖 Output: ./output/spreads.pdf"
echo "📚 Starting spreads from page: 3"
echo "🔍 DPI: 600"
echo ""

python3 create_spreads.py ./output/oma_jeanne_photobook_final.pdf -o ./output/spreads.pdf -s 3 -d 600

echo ""
echo "✅ Done! Check ./output/spreads.pdf for your spread version." 