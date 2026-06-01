#!/bin/bash
# ── CineMatch Startup Script ──────────────────────────────────────────────────
set -e

echo ""
echo "  ◈  CineMatch — Movie Recommendation System"
echo "  ─────────────────────────────────────────────"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "✗ Python 3 is required. Install it from https://python.org"
  exit 1
fi

# Create venv if not exists
if [ ! -d "venv" ]; then
  echo "→ Creating virtual environment..."
  python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install deps
echo "→ Installing dependencies..."
pip install -r requirements.txt -q

# Download NLTK data
echo "→ Downloading NLTK data..."
python3 -c "import nltk; nltk.download('punkt', quiet=True)"

# Init DB & start
echo "→ Starting server on http://localhost:5000"
echo ""
echo "  Open your browser at: http://localhost:5000"
echo ""
cd backend && python3 app.py
