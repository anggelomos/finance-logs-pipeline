import base64
from datetime import datetime
import json
from pathlib import Path
from typing import List

from openai import OpenAI

from finance_logs_pipeline.models import Transaction


class AIParser:
    """AI client for parsing transaction data."""
    
    def __init__(self, api_key: str, model: str):
        """Initialize the AI client."""
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def parse_image_statement(self, image_path: Path) -> List[Transaction]:
        """Parse transactions from a bank statement image using AI."""

        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        
        input_statement = {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                                }
                            ]
                        }

        return self._parse_transactions(input_statement)
    
    def parse_text_statement(self, text_path: Path) -> List[Transaction]:
        """Parse transactions from a bank statement text using AI."""

        with open(text_path, "r") as text_file:
            statements_text = text_file.read()

        input_statement = {
                            "role": "user",
                            "content": [
                                {
                                "type": "text",
                                "text": statements_text
                                }
                            ]
                        }

        return self._parse_transactions(input_statement)
    
    def _current_year(self) -> int:
        """Get the current year."""
        return datetime.now().year
    
    def _parse_transactions(self, input_statement: dict) -> List[Transaction]:
        """Parse transactions from text using AI."""

        response = self.client.chat.completions.create( # type: ignore[call-overload]
                model=self.model,
                messages=[
                    {
                    "role": "system",
                    "content": [
                        {
                        "type": "text",
                        "text": f"**Task:**  \nAct as an expert Data Entry specialist. You are provided with a bank statement that contains multiple transactions. Your task is to extract, parse, and format each transaction according to the instructions below.\n\n**Instructions:**  \n\n1. **Transaction Date:**  \n   - Extract the date of each transaction.\n   - Format the date as **MM/DD/YYYY**.\n   - If the year is missing, assume it is the current year, which is {self._current_year()}.\n\n2. **Transaction Description:**  \n   - Extract the description exactly as it appears.\n   - If the description is truncated, include only the visible text.\n\n3. **Transaction Value:**  \n   - Remove the \"$\" symbol and any cents.\n   - Convert the remaining value into an integer (without any punctuation).\n\n**Output Format:**  \n- Each transaction should appear on a new line.\n- Fields should be separated by a single comma.\n- The order of the fields must be: **Transaction Date, Transaction Description, Transaction Value**.\n- Do not include any extra spaces or trailing commas.\n- Only put the parsed transactions, not the original ones.\n- Put all the transactions in a single json schema"
                        }
                    ]
                    },
                    input_statement
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                    "name": "transactions",
                    "schema": {
                        "type": "object",
                        "required": [
                        "transactions"
                        ],
                        "properties": {
                        "transactions": {
                            "type": "array",
                            "items": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "A list of strings representing keywords for a single transaction."
                            },
                            "description": "A list of transactions, each containing a list of keywords as strings."
                        }
                        },
                        "additionalProperties": False
                    },
                    "strict": True
                    }
                },
                temperature=1,
                max_completion_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        
        raw_transactions = json.loads(response.choices[0].message.content)["transactions"]
        transactions = [Transaction(*transaction) for transaction in raw_transactions]
        
        return transactions
