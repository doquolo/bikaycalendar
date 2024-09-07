from bs4 import BeautifulSoup
import json

def tableToJS(innerHTML):
    soup = BeautifulSoup(innerHTML, 'html.parser')

    # Initialize the list to hold the JSON data
    table_data = []

    # Extract the headers
    headers = [th.get_text().strip() for th in soup.find_all('th')]

    # Extract the rows
    rows = soup.find_all('tr', class_='GridRow')
    for row in rows:
        data = {}
        cells = row.find_all('td')
        for i, cell in enumerate(cells):
            data[headers[i]] = cell.get_text().strip()
        table_data.append(data)

    # Convert the list to JSON
    return table_data
