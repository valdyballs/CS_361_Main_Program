from flask import Flask, request, jsonify, send_file
import requests
import csv
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class RentcastService:
    def __init__(self):
        self.api_key = "MY KEY MUAHAHAHAHAHA"
        self.base_url = "https://api.rentcast.io/v1"
        self.headers = {'X-Api-Key': self.api_key, 'Content-Type': 'application/json'}
        os.makedirs('data', exist_ok=True)

    def fetch_and_save_properties(self, city: str, state: str, limit: int = 100):
        try:
            response = requests.get(
                f"{self.base_url}/listings/sale",
                headers=self.headers,
                params={'city': city, 'state': state, 'limit': limit, 'status': 'Active'},
                timeout=30
            )
            response.raise_for_status()

            properties = self._process_properties(response.json(), city, state)
            filename = self._save_to_csv(properties, city, state)

            return {
                'success': True,
                'total_properties': len(properties),
                'filename': filename,
                'city': city,
                'state': state,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error: {e}")
            return {'success': False, 'error': str(e)}

    def _process_properties(self, raw_data, city, state):
        properties = []

        listings = []
        if isinstance(raw_data, dict):
            for key in ['listings', 'properties', 'data', 'results', 'items']:
                if key in raw_data and isinstance(raw_data[key], list):
                    listings = raw_data[key]
                    break
            if not listings and 'price' in raw_data:
                listings = [raw_data]
        elif isinstance(raw_data, list):
            listings = raw_data

        for listing in listings:
            # Skip land properties since we arent land barons! Buying a plot of land doesnt give you a house
            if listing.get('propertyType', '').lower() == 'land':
                continue

            property_data = {
                'address': self._format_address(listing),
                'price': listing.get('price', 0),
                'bedrooms': listing.get('bedrooms', listing.get('beds', 0)),
                'bathrooms': listing.get('bathrooms', listing.get('baths', 0)),
                'square_footage': listing.get('squareFootage', listing.get('sqft', 0)),
                'year_built': listing.get('yearBuilt', ''),
                'neighborhood': listing.get('neighborhood', ''),
                'property_type': listing.get('propertyType', ''),
                'listing_id': listing.get('id', ''),
                'city': listing.get('city', city),
                'state': listing.get('state', state),
                'zip_code': listing.get('zipCode', ''),
                'last_updated': datetime.now().isoformat()
            }

            if property_data['price'] > 0 and property_data['address']:
                properties.append(property_data)

        return properties

    def _format_address(self, listing):
        if 'formattedAddress' in listing:
            return listing['formattedAddress']
        if 'address' in listing:
            return listing['address']
        if 'addressLine1' in listing:
            return listing['addressLine1']

        parts = []
        for field in ['streetNumber', 'streetName', 'streetType']:
            if field in listing:
                parts.append(str(listing[field]))
        return ' '.join(parts) if parts else 'Address not available'

    def _save_to_csv(self, properties, city, state):
        filename = "properties.csv"
        filepath = f"data/{filename}"

        headers = [
            'address', 'price', 'bedrooms', 'bathrooms', 'square_footage',
            'year_built', 'neighborhood', 'property_type', 'listing_id',
            'city', 'state', 'zip_code', 'last_updated'
        ]

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(properties)

        with open("data/search_metadata.txt", 'w') as f:
            f.write(f"City: {city}\nState: {state}\nProperties: {len(properties)}\n")
            f.write(f"Updated: {datetime.now().isoformat()}\n")
        return filename

rentcast_service = RentcastService()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Rentcast Data Fetcher',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/fetch-city-data', methods=['POST'])
def fetch_city_data():
    data = request.get_json()
    if not data or not all([data.get('city'), data.get('state')]):
        return jsonify({'success': False, 'error': 'Missing city or state'}), 400

    result = rentcast_service.fetch_and_save_properties(
        data['city'], data['state'], data.get('limit', 100)
    )
    return jsonify(result)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    filepath = os.path.join('data', filename)
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'error': 'File not found'}), 404
    return send_file(filepath, as_attachment=True)


if __name__ == '__main__':
    print("Rentcast Data Fetcher Service")
    print("http://localhost:5003")
    print("Endpoints: /health, /fetch-city-data, /download/<filename>")
    app.run(debug=True, port=5003, host='0.0.0.0')