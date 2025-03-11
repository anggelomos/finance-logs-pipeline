import shutil
from pathlib import Path
from typing import List

from loguru import logger


from finance_logs_pipeline.config import config
from finance_logs_pipeline.models import Transaction
from finance_logs_pipeline.parsers.ai_parser import AIParser


class FileProcessor:
    """File processor for handling different file types."""
    
    def __init__(self, ai_parser: AIParser):
        """Initialize the file processor."""
        self.ai_parser = ai_parser

    @staticmethod
    def _clean_transaction(transaction: Transaction) -> Transaction:
        """Adjust the amount of a transaction."""

        transaction.amount = abs(transaction.amount)

        if transaction.amount > 1000:
            transaction.amount /= 1000
        return transaction
    
    def process_file(self, file_path: Path) -> List[Transaction]:
        """Process a file and extract transactions."""
        logger.info(f"Processing file: {file_path}")
        
        try:
            transactions = []
            if file_path.suffix.lower() == ".txt":
                transactions = self.ai_parser.parse_text_statement(file_path)
            elif file_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
                transactions = self.ai_parser.parse_image_statement(file_path)
            else:
                error_msg = f"Unsupported file type: {file_path.suffix}"
                logger.error(error_msg)
                return transactions
            
            if not transactions:
                logger.warning(f"No transactions found in file: {file_path}")

            # Then use it with map
            processed_transactions = list(map(
                self._clean_transaction,
                filter(lambda t: t.description not in config.excluded_keywords, transactions)
            ))
            
            return processed_transactions
            
        except Exception as e:
            error_msg = f"Error processing file {file_path}: {str(e)}"
            logger.error(error_msg)
            raise

    def archive_file(self, file_path: Path) -> Path:
        """Archive a file after processing."""
        destination = config.archive_dir / file_path.name        
        logger.info(f"Archiving file: {file_path} -> {destination}")

        shutil.move(str(file_path), str(destination))
        
        return destination
