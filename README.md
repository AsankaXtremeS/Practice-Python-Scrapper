# Walmart Product Scraper & Viewer

A complete web scraping solution to extract Walmart product data and display it in a beautiful, responsive web interface.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Web Scraper](#web-scraper)
  - [Frontend Viewer](#frontend-viewer)
- [Configuration](#configuration)
- [Output Format](#output-format)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Legal Notice](#legal-notice)
- [License](#license)

## ✨ Features

### Web Scraper (`walmart_scraper.py`)
- ✅ Scrapes Walmart product data from search results
- ✅ Extracts first 20 products for quick operation
- ✅ Collects: product name, price, brand, ratings, reviews, availability, images
- ✅ Handles multiple search queries automatically
- ✅ Proxy support (optional) for large-scale scraping
- ✅ Retry logic with exponential backoff
- ✅ Bot detection handling (HTTP 412 responses)
- ✅ Realistic browser headers to avoid blocking
- ✅ Respects server with 0.5s delays between requests

### Frontend Viewer (`index.html`)
- 🎨 Modern, responsive grid layout
- 📱 Mobile-friendly design
- 🖼️ Product image display with fallback
- 💰 Price, brand, and rating information
- ⭐ Star ratings and review counts
- 📦 Availability status with color coding
- 🎯 Interactive hover effects
- 📂 Easy file upload and parsing of JSONL data

## 📁 Project Structure

```
walmart-scraper/
├── walmart_scraper.py          # Main web scraper script
├── index.html                  # Frontend viewer
├── product_info.jsonl          # Output data (generated)
├── .gitignore                  # Git ignore file
├── .env                        # Environment variables (optional)
├── pyenv.cfg                   # Python environment config
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection

## 📥 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/walmart-scraper.git
cd walmart-scraper
```

### 2. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `requests` - HTTP library for web requests
- `beautifulsoup4` - HTML parsing library
- `python-dotenv` - Environment variable management (optional)

## 🚀 Usage

### Web Scraper

#### Basic Usage

```bash
python walmart_scraper.py
```

This will:
1. Search for products matching predefined queries: "computers", "laptops", "desktops", "monitors", "printers"
2. Scrape the first 20 products across all queries
3. Save data to `product_info.jsonl`
4. Display progress in the console

#### Modify Search Queries

Edit `walmart_scraper.py` and change the `SEARCH_QUERIES` list:

```python
SEARCH_QUERIES = ["your", "search", "terms", "here"]
```

#### Change Product Limit

Edit the `max_products` variable in the `main()` function:

```python
max_products = 50  # Increase from 20 to 50
```

#### Enable Proxy Support

Set `USE_PROXY = True` and configure your proxy credentials:

```python
USE_PROXY = True
```

Then create a `.env` file:

```
BRD_USERNAME=your_username
BRD_PASSWORD=your_password
```

### Frontend Viewer

#### Option 1: Open Directly (Recommended)
1. Open `index.html` in your web browser
2. Click "Choose File" and select your `product_info.jsonl`
3. Click "Load Products"
4. Browse your scraped data in the interactive grid

#### Option 2: Local Server

```bash
# Python 3+
python -m http.server 8000

# Then visit http://localhost:8000/index.html
```

## ⚙️ Configuration

### Scraper Settings

Edit `walmart_scraper.py` to customize:

| Setting | Location | Description |
|---------|----------|-------------|
| Search Queries | `SEARCH_QUERIES` | List of product searches |
| Output File | `OUTPUT_FILE` | Where to save data |
| Page Limit | `while page_number <= 2` | Pages per search |
| Product Limit | `max_products = 20` | Total products to scrape |
| Request Timeout | `timeout=10` | Seconds to wait for response |
| Retry Attempts | `max_retries = 5` | Attempts before giving up |

## 📊 Output Format

Data is saved as **JSONL** (JSON Lines - one JSON object per line):

```json
{"price": 299.99, "review_count": 150, "item_id": "12345", "avg_rating": 4.5, "product_name": "Dell Laptop", "brand": "Dell", "availability": "In Stock", "image_url": "https://...", "short_description": "High performance laptop"}
{"price": 899.99, "review_count": 320, "item_id": "12346", "avg_rating": 4.8, "product_name": "HP Desktop", "brand": "HP", "availability": "In Stock", "image_url": "https://...", "short_description": "Gaming desktop"}
```

## 📖 API Reference

### `extract_product_info(product_url)`

Extracts detailed product information from a Walmart product page.

**Parameters:**
- `product_url` (str): Full URL to Walmart product page

**Returns:**
- dict: Product information or None if extraction fails

**Raises:**
- HTTP 412: Bot detection; function returns None gracefully

### `get_product_links_from_search_page(query, page_number)`

Retrieves product links from Walmart search results.

**Parameters:**
- `query` (str): Search term
- `page_number` (int): Page number to scrape

**Returns:**
- list: URLs of products found on the page

## 🔍 Troubleshooting

### Issue: HTTP 412 Error (Bot Detection)

**Solution:** The scraper handles this automatically by:
- Using realistic browser headers
- Adding delays between requests
- Retrying with backoff
- Consider using a proxy (set `USE_PROXY = True`)

### Issue: No Products Found

**Check:**
1. Internet connection is active
2. Walmart.com is accessible
3. Search queries are valid
4. Try reducing page limits

### Issue: Images Not Loading in Frontend

**Possible Causes:**
- Image URL expired or blocked
- CORS restrictions
- Use a proxy or different image source

### Issue: File Upload Not Working

**Solutions:**
1. Ensure file is `.jsonl` format
2. Check browser console (F12) for errors
3. Verify JSONL is valid (one JSON object per line)
4. Try a different browser

## ⚖️ Legal Notice

**Important:** This tool is for educational purposes only. Before scraping:

1. **Review Walmart's Terms of Service** - Scraping may violate ToS
2. **Check `robots.txt`** - Respect scraping guidelines
3. **Rate Limiting** - The scraper includes delays to be respectful
4. **Use Responsibly** - Don't overload servers
5. **Proxy Responsibly** - If using proxies, ensure they're legitimate

By using this tool, you agree to use it ethically and legally.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👤 Author

Created as an educational web scraping project.

## 🙏 Acknowledgments

- BeautifulSoup4 for HTML parsing
- Requests library for HTTP handling
- All contributors and testers

## 📧 Support

For issues, questions, or suggestions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Open a GitHub issue
3. Create a discussion

---

**Happy Scraping!** 🎉

*Remember: Scrape responsibly and ethically.*
