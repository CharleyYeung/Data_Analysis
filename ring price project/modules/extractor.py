from bs4 import BeautifulSoup
import re

def extract_ring_details(html_content):
    """
    Parses HTML content to extract metal type, refcode, description, price, and image.
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    details_list = []

    try:
        # Get the main product image URL for the Excel/Exam reference
        img_tag = soup.select_one('.product-image img') or soup.find('img', {'id': 'main-image'})
        image_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else None

        # Process metal sections (based on your notebook's logic)
        metal_blocks = soup.find_all('h4')
        
        for h4 in metal_blocks:
            metal_name = h4.get_text(strip=True)
            table = h4.find_next('table')
            if not table: continue
                
            rows = table.find('tbody').find_all('tr') if table.find('tbody') else []
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    refcode = cells[0].get_text(strip=True)
                    description = cells[1].get_text(strip=True)
                    price = cells[2].get_text(strip=True)
                    
                    details_list.append({
                        'Metal': metal_name,
                        'Refcode': refcode,
                        'Description': description,
                        'Price': price,
                        'Image URL': image_url  # Storing for main file to download
                    })
    except Exception as e:
        print(f" Extraction Warning: {e}")
        
    return details_list