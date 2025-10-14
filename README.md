# Magical Background Remover

A powerful, user-friendly desktop application for removing backgrounds from images with AI and applying various effects. Built with Python and powered by machine learning.

## Features

### Core Functionality
- **AI-Powered Background Removal** - Automatically remove backgrounds using advanced ML models
- **Drag & Drop Support** - Simply drag images into the app
- **Batch Processing** - Process multiple images at once
- **Multi-Format Support** - Input: PNG, JPEG, BMP, WEBP, GIF | Output: PNG, JPEG, WEBP, BMP

### Image Effects
- **Magic Touch** 🪄 - Auto-enhance with brightness, contrast, sharpness, and gradient background
- **Blur Effect** 🌫️ - Apply Gaussian blur
- **Sharpen** 🔪 - Enhance image sharpness
- **Grayscale** ⚫ - Convert to black and white
- **Background Replacement** - Use solid colors or custom images as backgrounds

### User Experience
- **Modern UI** - Clean, intuitive interface with emoji indicators
- **Progress Indicators** - Real-time progress bars for long operations
- **Undo Functionality** - Revert changes with Ctrl+Z (up to 10 steps)
- **Keyboard Shortcuts** - Quick access to common functions
- **Responsive Design** - Resizable window that adapts to your screen

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download this repository**

2. **Install dependencies**
```bash
pip install -r Requirementsss.txt
```

3. **Run the application**
```bash
python program.py
```

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Upload Image |
| `Ctrl+S` | Save Output |
| `Ctrl+Z` | Undo |
| `F1` | Show Help |
| `ESC` | Exit Application |

## 📖 How to Use

### Single Image Processing

1. **Upload an Image**
   - Click "Upload Image" or press `Ctrl+O`
   - Or drag and drop an image directly onto the input area

2. **Remove Background**
   - Click "Remove Background"
   - Wait for the AI to process (progress bar will show)

3. **Apply Effects (Optional)**
   - Choose from various effects in the "Effects & Tools" section
   - Apply multiple effects - each can be undone

4. **Save Your Work**
   - Select output format (PNG, JPEG, WEBP, or BMP)
   - Click "💾 Save Output" or press `Ctrl+S`

### Batch Processing

1. Click "Batch Process"
2. Select multiple images
3. Choose an output directory
4. Wait for processing to complete
5. All images will be saved with "_nobg" suffix

### Background Replacement

1. Remove background first
2. Choose replacement method:
   - **Replace BG Color** - Pick a solid color
   - **Replace BG Image** - Use another image as background

## Tips & Tricks

- **Best Results**: Use high-quality images with clear subject-background separation
- **Multiple Effects**: Apply effects one at a time for better control
- **Undo**: Made a mistake? Press `Ctrl+Z` to undo (works for up to 10 steps)
- **Batch Processing**: Perfect for processing product photos, profile pictures, etc.
- **Format Selection**: Use PNG for transparency, JPEG for smaller file sizes

## 👨‍💻 Developer

**Hassan Ahmed**  
Developed for Hack Club, Enjoy removing backgrounds magically ;)

## 📄 License

This project is open source and available for educational purposes.
For issues or questions, please check the Help menu (F1) or refer to this README.
