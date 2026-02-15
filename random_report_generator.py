#!/usr/bin/env python3
import random
from datetime import datetime, timedelta

def generate_random_bill():
    # Random invoice number
    invoice_num = f"INV-{random.randint(2020, 2024)}-{random.randint(1, 9999):04d}"
    
    # Random dates
    start_date = datetime.now() - timedelta(days=random.randint(0, 365))
    date_str = start_date.strftime("%Y-%m-%d")
    due_date_str = (start_date + timedelta(days=random.randint(15, 60))).strftime("%Y-%m-%d")
    
    # Random customer
    company_types = ["Corp", "LLC", "Inc", "Ltd", "Group", "Solutions", "Systems", "Technologies"]
    company_names = ["Acme", "Global", "Tech", "Prime", "Elite", "Mega", "Alpha", "Beta", "Omega", 
                     "Quantum", "Nexus", "Vertex", "Apex", "Summit", "Fusion"]
    company_name = f"{random.choice(company_names)} {random.choice(company_types)}"
    
    street_num = random.randint(100, 9999)
    street_names = ["Main", "Oak", "Maple", "Cedar", "Park", "Business", "Commerce", "Industrial"]
    street_types = ["St", "Ave", "Blvd", "Dr", "Way", "Rd"]
    suite = f"Suite {random.randint(100, 999)}" if random.random() > 0.5 else ""
    
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", 
              "San Antonio", "San Diego", "Dallas", "Austin"]
    states = ["NY", "CA", "IL", "TX", "AZ", "PA", "FL", "OH", "NC", "GA"]
    
    address = f"{street_num} {random.choice(street_names)} {random.choice(street_types)}"
    if suite:
        address += f", {suite}"
    address += f"\n{random.choice(cities)}, {random.choice(states)} {random.randint(10000, 99999)}"
    
    # Random items
    services = [
        ("Consulting Services", (50, 200), (5, 40)),
        ("Software License", (100, 2000), (1, 10)),
        ("Support Hours", (75, 150), (1, 20)),
        ("Development Services", (80, 250), (10, 100)),
        ("Training Sessions", (100, 300), (1, 5)),
        ("Maintenance Contract", (500, 5000), (1, 12)),
        ("Cloud Hosting", (50, 500), (1, 12)),
        ("API Access", (100, 1000), (1, 1)),
        ("Custom Integration", (150, 400), (5, 50)),
        ("Security Audit", (200, 500), (1, 3)),
        ("Database Management", (100, 300), (10, 50)),
        ("Project Management", (120, 280), (5, 30))
    ]
    
    num_items = random.randint(1, 6)
    selected_services = random.sample(services, num_items)
    
    items = []
    for service_name, price_range, qty_range in selected_services:
        items.append({
            "description": service_name,
            "quantity": random.randint(*qty_range),
            "unit_price": round(random.uniform(*price_range), 2)
        })
    
    # Random tax rate
    tax_rate = round(random.uniform(0.05, 0.12), 3)
    
    return {
        "invoice_number": invoice_num,
        "date": date_str,
        "due_date": due_date_str,
        "customer": {
            "name": company_name,
            "address": address
        },
        "items": items,
        "tax_rate": tax_rate
    }

if __name__ == "__main__":
    # Generate 5 random bills
    for i in range(5):
        bill = generate_random_bill()
        print(f"\nBill {i+1}:")
        print(bill)