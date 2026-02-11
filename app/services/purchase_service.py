import time
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Item


def purchase(db: Session, item_id: str, cash_inserted: int) -> dict:
    try:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise ValueError("item_not_found")

        if cash_inserted < item.price:
            raise ValueError("insufficient_cash", item.price, cash_inserted)

        rows_updated = (
            db.query(Item)
            .filter(Item.id == item_id, Item.quantity > 0)
            .update({Item.quantity: Item.quantity - 1})
        )

        if rows_updated == 0:
            raise ValueError("out_of_stock")

        db.query(type(item.slot)).filter(
            type(item.slot).id == item.slot_id
        ).update({
            type(item.slot).current_item_count:
            type(item.slot).current_item_count - 1
        })

        db.commit()

        remaining_quantity = (
            db.query(Item.quantity)
            .filter(Item.id == item_id)
            .scalar()
        )

        return {
            "item": item.name,
            "price": item.price,
            "cash_inserted": cash_inserted,
            "change_returned": cash_inserted - item.price,
            "remaining_quantity": remaining_quantity,
            "message": "Purchase successful",
        }

    except:
        db.rollback()
        raise



def change_breakdown(change: int) -> dict:
    denominations = sorted(settings.SUPPORTED_DENOMINATIONS, reverse=True)
    result: dict[str, int] = {}
    remaining = change
    for d in denominations:
        if remaining <= 0:
            break
        count = remaining // d
        if count > 0:
            result[str(d)] = count
            remaining -= count * d
    return {"change": change, "denominations": result}

