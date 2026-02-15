#!/usr/bin/env python3
import csv
from datetime import datetime


def generate_invoice_csv(billing_data, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(["INVOICE"])
        writer.writerow([])

        # Invoice details
        writer.writerow(["Invoice #:", billing_data.get("invoice_number", "N/A")])
        writer.writerow(["Date:", billing_data.get("date", datetime.now().strftime("%Y-%m-%d"))])
        writer.writerow(["Due Date:", billing_data.get("due_date", "N/A")])
        writer.writerow([])

        # Bill to section
        writer.writerow(["Bill To:"])
        customer = billing_data.get("customer", {})
        writer.writerow([customer.get("name", "N/A")])
        for line in (customer.get("address", "N/A") or "").split("\n"):
            writer.writerow([line])
        writer.writerow([])

        # Line items
        items = billing_data.get("items", [])
        writer.writerow(["Description", "Quantity", "Unit Price", "Amount"])

        for item in items:
            amount = item.get("quantity", 0) * item.get("unit_price", 0)
            writer.writerow([
                item.get("description", ""),
                item.get("quantity", 0),
                f"${item.get('unit_price', 0):.2f}",
                f"${amount:.2f}",
            ])
        writer.writerow([])

        # Totals
        subtotal = sum(item.get("quantity", 0) * item.get("unit_price", 0) for item in items)
        tax_rate = billing_data.get("tax_rate", 0)
        tax = subtotal * tax_rate
        total = subtotal + tax

        writer.writerow(["Subtotal:", f"${subtotal:.2f}"])
        writer.writerow([f"Tax ({tax_rate * 100:.1f}%):", f"${tax:.2f}"])
        writer.writerow(["Total:", f"${total:.2f}"])

    return output_path


# Example usage
if __name__ == "__main__":
    sample_payload = {
        "invoice_number": "INV-2024-001",
        "date": "2024-02-14",
        "due_date": "2024-03-14",
        "customer": {
            "name": "Acme Corporation",
            "address": "123 Business St, Suite 100\nCity, ST 12345",
        },
        "items": [
            {"description": "Consulting Services", "quantity": 10, "unit_price": 150.00},
            {"description": "Software License", "quantity": 1, "unit_price": 500.00},
            {"description": "Support Hours", "quantity": 5, "unit_price": 100.00},
        ],
        "tax_rate": 0.08,
    }

    generate_invoice_csv(sample_payload, "invoice.csv")
    print("CSV generated: invoice.csv")
