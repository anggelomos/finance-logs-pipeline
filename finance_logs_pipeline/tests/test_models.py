"""Tests for the models module."""


import pytest

from finance_logs_pipeline.models import Transaction, TransactionType, ProcessingResult


@pytest.mark.parametrize(
    "date_str, amount, description, expected_success",
    [
        # Valid date format
        ("01/15/2023", 100.50, "Test transaction 1", True),
        ("3/8/2023", 200.75, "Test transaction 2", True),
        ("12/31/2023", 50.00, "Test transaction 3", True),
        
        # Invalid date format - these should raise ValueError
        ("2023-01-15", 300.25, "Invalid format 1", False),
        ("15/01/2023", 400.00, "Invalid format 2", False),
        ("Jan 15, 2023", 500.50, "Invalid format 3", False),
    ]
)
def test_transaction_creation(date_str, amount, description, expected_success):
    """Test that transactions can be created with various inputs."""
    if expected_success:
        # Should succeed
        transaction = Transaction(
            date=date_str,
            amount=amount,
            description=description,
        )
        
        assert transaction.date == date_str
        assert transaction.amount == amount
        assert transaction.description == description
        assert transaction.transaction_type == TransactionType.UNPROCESSED
    else:
        # Should fail with ValueError
        with pytest.raises(ValueError):
            Transaction(
                date=date_str,
                amount=amount,
                description=description,
            )

def test_processing_result():
    """Test that a processing result can be created."""
    transaction = Transaction(
        date="01/15/2023",
        amount=100.50,
        description="Test transaction",
    )
    
    result = ProcessingResult(
        filename="test.txt",
        transactions=[transaction]
    )
    
    assert result.filename == "test.txt"
    assert len(result.transactions) == 1
    assert result.success is True
    assert result.error is None 
