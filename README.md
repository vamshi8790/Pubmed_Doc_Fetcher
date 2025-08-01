# PubMed Research Paper Fetcher

A Python program that fetches research papers from PubMed based on user-specified queries and identifies papers with at least one author affiliated with a pharmaceutical or biotech company.

## Features

- **PubMed API Integration**: Fetches papers using the official NCBI E-utilities API
- **Company Affiliation Detection**: Identifies authors affiliated with pharmaceutical/biotech companies using keyword matching and heuristics
- **Full Query Support**: Supports PubMed's complete query syntax for flexible searching
- **CSV Export**: Returns results in a structured CSV format with all required columns
- **Command-line Interface**: Easy-to-use CLI with multiple options
- **Rate Limiting**: Respects NCBI API guidelines with proper rate limiting
- **Error Handling**: Robust error handling for API failures and data parsing issues

## Installation

### Prerequisites

- Python 3.8 or higher
- Poetry (for dependency management)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/pubmed-paper-fetcher.git
   cd pubmed-paper-fetcher
   ```

2. **Install dependencies using Poetry:**
   ```bash
   poetry install
   ```

3. **Activate the virtual environment:**
   ```bash
   poetry shell
   ```

## Usage

### Command Line Interface

The program provides a command-line tool called `get-papers-list` that you can use after installation:

```bash
get-papers-list "cancer immunotherapy"


get-papers-list "CRISPR gene editing" --max-results 50 --output results.csv


get-papers-list "COVID-19 vaccine" --debug --email your.email@example.com
```

### Command-line Options

- `query`: Search query for PubMed (required)
- `-f, --file`: Output CSV filename (default: `research_papers.csv`)
- `-d, --debug`: Print debug information during execution
- `-h, --help`: Display usage instructions
- `--max-results`: Maximum number of papers to fetch (default: 100)
- `--email`: Email address for NCBI API identification (default: user@example.com)
- `--api-key`: NCBI API key for increased rate limits (optional)

### Examples

1. **Search for cancer research papers:**
   ```bash
   get-papers-list "cancer immunotherapy"
   ```

2. **Search with specific author:**
   ```bash
   get-papers-list "Smith JA[Author] AND cancer"
   ```

3. **Search with date range:**
   ```bash
   get-papers-list "COVID-19 vaccine" --max-results 200
   ```

4. **Search with custom output file:**
   ```bash
   get-papers-list "gene therapy" --file gene_therapy_papers.csv
   ```

## Output Format

The program generates a CSV file with the following columns:

- **PubmedID**: Unique identifier for the paper
- **Title**: Title of the paper
- **Publication Date**: Date the paper was published (YYYY-MM-DD format)
- **Non-academic Author(s)**: Names of authors affiliated with non-academic institutions
- **Company Affiliation(s)**: Names of pharmaceutical/biotech companies
- **Corresponding Author Email**: Email address of the corresponding author

## Code Organization

The project is organized into two main modules:

### `pubmed_fetcher.py`
The core module containing:
- `PubMedFetcher` class: Main class for API interactions and data processing
- `PaperInfo` dataclass: Data structure for storing paper information
- Company affiliation detection logic
- CSV export functionality

### `pubmed_cli.py`
Command-line interface module containing:
- Argument parsing with `argparse`
- User-friendly error messages
- Debug output options
- Integration with the core fetcher module

## Company Detection Algorithm

The program identifies pharmaceutical/biotech company affiliations using:

1. **Keyword Matching**: Searches for common company names and industry terms
2. **Heuristic Analysis**: Identifies corporate identifiers (Inc., Ltd., Corp., etc.)
3. **Academic Exclusion**: Filters out typical academic institutions (universities, hospitals, research centers)

### Recognized Company Keywords
- Major pharmaceutical companies (Pfizer, Roche, Novartis, Merck, etc.)
- Biotech companies (Amgen, Gilead, Biogen, Moderna, etc.)
- Generic industry terms (pharmaceutical, biotechnology, biotech, pharma)
- Corporate identifiers (Inc., Ltd., Corp., Corporation, Limited)

## API Rate Limiting

The program respects NCBI's API guidelines:
- Maximum 3 requests per second without API key
- Maximum 10 requests per second with API key
- Automatic batching for large result sets
- Proper error handling and retry logic

## Error Handling

The program includes comprehensive error handling for:
- Network connectivity issues
- API rate limiting and timeouts
- XML parsing errors
- Invalid query syntax
- Missing or malformed data

## Development Tools

The project uses modern Python development tools:
- **Poetry**: Dependency management and packaging
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing framework

## Development Setup

1. **Install development dependencies:**
   ```bash
   poetry install --with dev
   ```

2. **Run code formatting:**
   ```bash
   poetry run black .
   poetry run isort .
   ```

3. **Run linting:**
   ```bash
   poetry run flake8
   ```

4. **Run type checking:**
   ```bash
   poetry run mypy pubmed_fetcher.py pubmed_cli.py
   ```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NCBI for providing the PubMed API
- The scientific community for making research accessible
- Contributors and users of this tool

## Support

If you encounter any issues or have questions, please:
1. Check the existing issues on GitHub
2. Create a new issue with detailed information
3. Include debug output when reporting problems

## API Compliance

This tool complies with NCBI's E-utilities usage guidelines:
- Includes email identification in all requests
- Respects rate limiting requirements
- Uses appropriate query parameters
- Handles errors gracefully