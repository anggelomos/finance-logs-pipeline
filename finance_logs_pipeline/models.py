from datetime import datetime
from enum import Enum
from typing import List, Optional

from attrs import define, field
from tickthon import ExpenseLog

def validate_date_format(instance, attribute, value):
    """Validate date string has format M/D/YYYY."""
    try:
        datetime.strptime(value, "%m/%d/%Y")
    except ValueError:
        raise ValueError(f"Date '{value}' doesn't match format M/D/YYYY")

class TransactionType(str, Enum):
    """Transaction type enum."""
    
    UNPROCESSED = "unprocessed"


@define
class Transaction:
    """Transaction model.
    
    Attributes:
        date: date of the transaction with the format M/D/YYYY
        transaction_type: type of the transaction
        amount: amount of the transaction
        description: description of the transaction
    """
    
    date: str = field(validator=validate_date_format)
    description: str = field()
    amount: float = field(converter=float)
    transaction_type: TransactionType = field(default=TransactionType.UNPROCESSED)

    def to_expense_log(self) -> ExpenseLog:
        """Convert Transaction to ExpenseLog."""

        date = datetime.strptime(self.date, "%m/%d/%Y").strftime("%Y-%m-%d")

        return ExpenseLog(
            date=date,
            product=self.description,
            expense=self.amount,
        )

@define
class ProcessingResult:
    """Result of processing a file."""
    
    filename: str = field()
    transactions: List[Transaction] = field()
    error: Optional[str] = field(default=None)
    success: bool = field(default=True) 
