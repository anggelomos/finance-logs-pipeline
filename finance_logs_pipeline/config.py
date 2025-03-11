from datetime import datetime
import os
from pathlib import Path
import sys
from typing import List
import json

from rich.console import Console
from rich.panel import Panel
from attrs import define, field
from loguru import logger


ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_FILE_PATH = ROOT_DIR / "config.json"
INPUT_DIR = ROOT_DIR / "statements"
ARCHIVE_DIR = ROOT_DIR / "statements" / "archive"
LOGS_DIR = ROOT_DIR / "logs"

for directory in [INPUT_DIR, ARCHIVE_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


@define
class AppConfig:
    """Main application configuration."""
    
    # API Keys
    openai_api_key: str = field(factory=lambda: os.getenv("OAI_AUTH", ""))
    notion_api_key: str = field(factory=lambda: os.getenv("NT_AUTH", ""))
    notion_database_id: str = field(factory=lambda: os.getenv("NT_EXPENSES_DB_ID", ""))
    
    # Directories
    input_dir: Path = field(default=INPUT_DIR)
    archive_dir: Path = field(default=ARCHIVE_DIR)
    logs_dir: Path = field(default=LOGS_DIR)
    
    # Processing settings
    excluded_keywords: List[str] = field(
        factory=list,
        metadata={"description": "Keywords to exclude from transaction processing"}
    )
    default_transaction_type: str = field(default="unprocessed")    
    ai_model: str = field(default="")


def load_config() -> AppConfig:
    """Load configuration from file or create default."""

    if CONFIG_FILE_PATH.exists():
        with open(CONFIG_FILE_PATH, "r") as f:
            config = json.load(f)
    else:
        raise FileNotFoundError(f"Configuration file not found at: {CONFIG_FILE_PATH}")
    
    excluded_keywords = config.get("excluded_keywords", [])
    ai_model = config.get("ai_model", "")
    config = AppConfig(excluded_keywords=excluded_keywords, ai_model=ai_model)
    
    return config

def setup_logger():
    """Set up the logger."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = config.logs_dir / f"finance_logs_{timestamp}.log"
    
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add(log_file, level="DEBUG", rotation="10 MB")
    
    return log_file


def validate_environment():
    """Validate that all required environment variables are set."""
    console = Console()
    
    missing_vars = []
    if not config.openai_api_key:
        missing_vars.append("OPENAI_API_KEY")
    if not config.notion_api_key:
        missing_vars.append("NOTION_API_KEY")
    if not config.notion_database_id:
        missing_vars.append("NOTION_DATABASE_ID")
    
    if missing_vars:
        console.print(Panel.fit(
            f"[bold red]Missing required environment variables:[/bold red] {', '.join(missing_vars)}\n"
            "Please set these variables in a .env file or in your environment.",
            title="Environment Error"
        ))
        return False
    
    return True


config = load_config()
