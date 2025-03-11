from pathlib import Path

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from nothion import NotionClient

from finance_logs_pipeline.parsers.ai_parser import AIParser
from finance_logs_pipeline.config import config, setup_logger, validate_environment
from finance_logs_pipeline.parsers.file_processor import FileProcessor


def process_files(file_processor: FileProcessor, notion_uploader: NotionClient):
    """Process files and upload transactions to Notion."""
    console = Console()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        extensions = ["*.txt", "*.png", "*.jpg", "*.jpeg"]
        files = [file for ext in extensions for file in config.input_dir.glob(ext)]
        total_transactions = 0

        processing_task = progress.add_task("[cyan]Processing files...", total=len(files))
        
        if files:
            for file_path in files:
                transactions = file_processor.process_file(Path(file_path))
                
                for transaction in transactions:
                    notion_uploader.expenses.add_expense_log(transaction.to_expense_log())

                file_processor.archive_file(file_path)
                progress.update(processing_task, advance=1)
                total_transactions += len(transactions)

        else:
            raise FileNotFoundError("No files found in the input directory.")
        
        progress.update(processing_task, completed=True, total=1)
        
    
    console.print(Panel.fit(
        f"[bold green]Successfully processed {len( files)} files[/bold green]\n"
        f"[bold green]Uploaded {total_transactions} transactions to Notion[/bold green]",
        title="Summary"
    ))


def main():
    """Main entry point for the finance logs pipeline."""
    console = Console()
    console.print(Panel.fit("Finance Logs Pipeline", title="Starting"))
    
    log_file = setup_logger()
    logger.info("Starting Finance Logs Pipeline")
    
    if not validate_environment():
        return
    
    try:
        ai_parser = AIParser(config.openai_api_key, config.ai_model)
        notion_uploader = NotionClient(config.notion_api_key, expenses_db_id=config.notion_database_id)
        file_processor = FileProcessor(ai_parser)
        
        console.print("Verifying Notion database access...")
        
        process_files(file_processor, notion_uploader)
        
        logger.info("Finance Logs Pipeline completed successfully")
        console.print(f"\n[dim]Log file: {log_file}[/dim]")
        
    except Exception as e:
        logger.exception(f"Error in Finance Logs Pipeline: {e}")
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        console.print(f"\n[dim]Check log file for details: {log_file}[/dim]")


if __name__ == "__main__":
    main()
