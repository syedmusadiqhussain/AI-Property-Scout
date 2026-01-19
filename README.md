# AI Property Scout

An intelligent property search and analysis application that helps users find properties using AI-powered search and data extraction.

## Features

- **Property Search**: Search for properties using natural language queries via Google Search API
- **Data Extraction**: Extract property details from web pages using headless browser technology
- **AI Analysis**: Analyze property data using Hugging Face AI models
- **Full Cycle Automation**: Complete property search, extraction, and analysis workflow
- **Web Interface**: User-friendly web interface built with Flask and vanilla JavaScript
- **MCP Server**: Model Context Protocol server for integration with AI assistants

## Architecture

The project consists of two main components:

1. **Flask Web Application** (`app.py`): Main web server with REST API endpoints
2. **MCP Server** (`property-scout-server/`): TypeScript-based MCP server for AI assistant integration

## Prerequisites

- Python 3.8+
- Node.js 16+ (for MCP server)
- API Keys for:
  - Serper.dev (Google Search API)
  - Browserless.io (Headless browser)
  - Hugging Face (AI models)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/syedmusadiqhussain/AI-Property-Scout.git
   cd AI-Property-Scout
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   SERPER_API_KEY=your_serper_api_key
   BROWSERLESS_API_KEY=your_browserless_api_key
   HUGGINGFACE_API_KEY=your_huggingface_api_key
   ```

4. **Install MCP server dependencies (optional):**
   ```bash
   cd property-scout-server
   npm install
   cd ..
   ```

## Usage

### Running the Flask Web Application

1. **Start the server:**
   ```bash
   python app.py
   ```

2. **Open your browser and navigate to:**
   ```
   http://127.0.0.1:5000
   ```

3. **Use the web interface:**
   - Enter a property search query (e.g., "10 Marla house DHA Phase 6 under 5 Crore")
   - Click "Search Properties" to find listings
   - Click "Extract Data" on any result to scrape property details
   - Click "Find House (Full Cycle)" for automated search, extraction, and analysis

### API Endpoints

- `GET /` - Main web interface
- `POST /search` - Search for properties
- `POST /extract` - Extract data from a URL
- `POST /analyze` - Analyze property text
- `GET /find_house` - Complete property search workflow

### Running the MCP Server (Optional)

```bash
cd property-scout-server
npm run build
npm start
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SERPER_API_KEY` | Serper.dev API key for Google search | Yes |
| `BROWSERLESS_API_KEY` | Browserless.io API key for web scraping | Yes |
| `HUGGINGFACE_API_KEY` | Hugging Face API key for AI analysis | Yes |

## API Keys Setup

1. **Serper.dev**: Get your API key from [serper.dev](https://serper.dev)
2. **Browserless.io**: Get your API key from [browserless.io](https://browserless.io)
3. **Hugging Face**: Get your API key from [huggingface.co](https://huggingface.co/settings/tokens)

## Project Structure

```
AI Property Scout/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Web interface
├── property-scout-server/     # MCP server (optional)
│   ├── server.py              # Python MCP server
│   ├── src/
│   │   └── property-scout-server/
│   │       └── index.ts       # TypeScript MCP server
│   ├── package.json
│   ├── tsconfig.json
│   └── requirements.txt
├── .gitignore
└── README.md
```

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **APIs**: Serper, Browserless, Hugging Face
- **MCP Server**: TypeScript/Node.js (optional)
- **Web Scraping**: Headless browser automation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

syedmusadiqhussain9@gmail.com
