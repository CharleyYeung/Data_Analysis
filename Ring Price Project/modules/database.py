import sqlite3
import os
import logging

def init_db(db_path='data/jewelry.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS products')
    cursor.execute('DROP TABLE IF EXISTS price_history')
    
    # Create table with EXACT names from Excel to ensure Notebook compatibility
    cursor.execute('''
        CREATE TABLE products (
            "Image" TEXT,
            "Reference" TEXT PRIMARY KEY,
            "Price" REAL,
            "Series:" TEXT,
            "Model:" TEXT,
            "Model Variant:" TEXT,
            "Category:" TEXT,
            "Style Type:" TEXT,
            "Alloy:" TEXT,
            "Range:" TEXT,
            "Shank Profile:" TEXT,
            "Shank Style:" TEXT,
            "Setting Claw Type:" TEXT,
            "Setting Style:" TEXT,
            "Guide Weight:" TEXT,
            "Stone Type:" TEXT,
            "Stone Quantity:" TEXT,
            "Stone Shape:" TEXT,
            "Stone Size (mm):" TEXT,
            "Stone Size (ct):" TEXT,
            "Stone Description:" TEXT,
            "Diamond Round / Brilliant Cut - Various mm:" TEXT,
            "£ Per g" REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            refcode TEXT,
            price REAL,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (refcode) REFERENCES products ("Reference")
        )
    ''')
    conn.commit()
    conn.close()

def save_to_sql(all_details, db_path='data/jewelry.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for item in all_details:
        ref = item.get('Reference')
        if not ref: continue
        
        try:
            # Insert ALL 22 columns to mirror the Excel exactly
            cursor.execute('''
                INSERT OR REPLACE INTO products (
                    "Image", "Reference", "Price", "Series:", "Model:", "Model Variant:",
                    "Category:", "Style Type:", "Alloy:", "Range:", "Shank Profile:",
                    "Shank Style:", "Setting Claw Type:", "Setting Style:", "Guide Weight:",
                    "Stone Type:", "Stone Quantity:", "Stone Shape:", "Stone Size (mm):",
                    "Stone Size (ct):", "Stone Description:", "Diamond Round / Brilliant Cut - Various mm:", "£ Per g"
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (
                item.get('Image'), item.get('Reference'), item.get('Price'), 
                item.get('Series:'), item.get('Model:'), item.get('Model Variant:'),
                item.get('Category:'), item.get('Style Type:'), item.get('Alloy:'),
                item.get('Range:'), item.get('Shank Profile:'), item.get('Shank Style:'),
                item.get('Setting Claw Type:'), item.get('Setting Style:'), item.get('Guide Weight:'),
                item.get('Stone Type:'), item.get('Stone Quantity:'), item.get('Stone Shape:'),
                item.get('Stone Size (mm):'), item.get('Stone Size (ct):'), item.get('Stone Description:'),
                item.get('Diamond Round / Brilliant Cut - Various mm:'), item.get('£ Per g')
            ))

            # Still keep price_history for time-series showcase
            cursor.execute('INSERT INTO price_history (refcode, price) VALUES (?, ?)', (ref, item.get('Price')))
            
        except Exception as e:
            logging.error(f"Error processing {ref}: {e}")

    conn.commit()
    conn.close()