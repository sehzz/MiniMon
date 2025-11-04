from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class Category(int, Enum):
    """
    Different categories of transactions.

    Possible values:
    - GROCERIES: Groceries.
    - TRANSPORTATION: Transportation.
    - CLOTHING: Clothing.
    - RESTAURANTS: Restaurants.
    - FAMILY: Family.
    - OFFICE_BUSINESS: Office and business.
    - OTHERS: Others.
    - SUBSCRIPTIONS: Subscriptions.
    """
    GROCERIES = 1
    TRANSPORTATION = 2
    CLOTHING = 3
    RESTAURANTS = 4
    FAMILY = 5
    OFFICE_BUSINESS = 6
    OTHERS = 7
    SUBSCRIPTIONS = 8

class GrocerySubCategory(int, Enum):
    """
    Different subcategories of groceries.

    Possible values:
    - LIDL: LIDL.
    - KAUFLAND: Kaufland.
    - ALDI: Aldi.
    - PENNY: Penny.
    - REWE: Rewe.
    """
    LIDL = 8
    KAUFLAND = 9
    ALDI = 10
    PENNY = 11
    REWE = 12


class Transaction(BaseModel):
    id: int
    description: str
    amount: float
    transaction_date: str
    category_id: int
    created_at: str
    user_id: Optional[str] = None


#TODO make default functions to get table data from supabase and store them as obj(Transaction)


