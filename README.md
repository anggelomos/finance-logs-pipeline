## Finance Logs Pipeline

Automated expense transaction ingestion from multiple sources to Notion. This tool processes transaction data from text files or images, extracts relevant information using OpenAI's API, and uploads transactions to a specified Notion database.

## Installation

Clone the repository:
```sh
git clone https://github.com/yourusername/finance-logs-pipeline.git
cd finance-logs-pipeline
```

Install dependencies using Poetry:
```sh
poetry install
```

Setup environment variables with your API keys:
```sh
OPENAI_API_KEY=your_openai_api_key
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_notion_database_id
```

## Usage

Process transaction files:
```sh
poetry run finance-logs
```

## How It Works

1. The pipeline scans the input directory for transaction files (`*.txt`, `*.png`, `*.jpg`, `*.jpeg`).
2. For each file:
   - An AI parser (using OpenAI) extracts transaction details.
   - Transactions are uploaded to a Notion database.
   - Processed files are moved to an archive directory.

## Configuration

The application uses a `config.json` file and environment variables for configuration:
- Processing settings like excluded keywords
- Name of the AI model you want to use to process the files

## Compiling with PyInstaller

To create a standalone executable:
```sh
poetry run pyinstaller --name finance_logs_pipeline --add-data "finance_logs_pipeline:finance_logs_pipeline" finance_logs_pipeline/main.py
```
