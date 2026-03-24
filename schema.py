from pydantic import BaseModel, Field
from typing import Optional

class Transaction(BaseModel):
    """
    Schema for a transaction request.
    """
    transaction_id: Optional[str] = Field(None, description="Unique identifier for the transaction")
    user_id: str = Field(..., description="The ID of the user performing the transaction")
    amount: float = Field(..., gt=0, description="The transaction amount (must be positive)")
    currency: str = Field("USD", min_length=3, max_length=3, description="3-letter currency code")
    description: Optional[str] = Field(None, max_length=100, description="Optional transaction notes")
