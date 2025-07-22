import requests
import sys
import time
import pandas as pd
import os
from datetime import datetime
import zmq
import json


class HomeBuyerCLI:
    def __init__(self):
        self.user_location = None
        self.user_budget = None
        self.search_results = []
        self.current_city = None
        self.current_state = None
        self.service_url = "http://localhost:5003"

        # Simple ZMQ setup for Kelsey's validation service
        self.context = zmq.Context()
        self.socket = None
        try:
            self.socket = self.context.socket(zmq.REQ)
            self.socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 second timeout
            self.socket.connect("tcp://localhost:5555")
            print("Connected to validation service")
        except:
            print("Validation service not available, using basic validation")

    def save_budget(self, amount):
        """Save my users budget to a text file so my brothers and sisters can sort and dort"""
        with open('downpayment.txt', 'w') as f:
            f.write(f"{amount}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    def display_welcome(self):
        """Say what up to my user on god"""
        print("=" * 60)
        print("                HOME FINDER CLI")
        print("       Find Homes Within Your Budget")
        print("=" * 60)
        print("Loading... Dataset: 125,847 properties from 50 states")
        time.sleep(1)
        print("Ready for Action!")
        input("Press Enter to continue...")

    def main_menu(self):
        while True:
            print("\n" + "=" * 60)
            print("                MAIN MENU")
            print("=" * 60)
            print("[1] Start Home Search")
            print("[2] Help")
            print("[3] Quit")

            choice = input("Choice (1-3): ").strip()
            if choice == "1":
                self.home_search()
            elif choice == "2":
                self.show_help()
            elif choice == "3":
                self.quit_app()
                break
            else:
                print("Invalid choice.")

    def home_search(self):
        if self.get_location() and self.get_budget():
            self.search_properties()

    def get_location(self):
        print("\n" + "=" * 60)
        print("                LOCATION SETUP")
        print("=" * 60)
        print(
            "You will first be asked to enter the city you wish to live (Example: Seattle) we will ask for the state next (Example: WA)")

        city = input("City: ").strip()
        state = input("State (2-letter): ").strip().upper()

        # Use Kelsey's validation service if available
        if self.socket:
            try:
                print("Validating with partner's service...")
                request = {"city": city, "state": state}
                self.socket.send_string(json.dumps(request))
                response = self.socket.recv()
                result = json.loads(response.decode())

                if result['valid']:
                    print(f"Validation successful: {result['formatted_location']}")
                    self.current_city = result['city']
                    self.current_state = result['state']
                    self.user_location = result['formatted_location']
                    return True
                else:
                    print(f"{result['error']}")
                    if 'suggestion' in result:
                        print(f"💡 {result['suggestion']}")
                    return False

            except Exception as e:
                print(f"Validation service error: {e}")
                print("Using basic validation...")

        # Fallback to original validation if service unavailable
        valid_states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        }

        if not city or state not in valid_states:
            print("Invalid city or state")
            return False

        self.current_city = city
        self.current_state = state
        self.user_location = f"{city}, {state}"
        return True

    def get_budget(self):
        print("\n" + "=" * 60)
        print("                BUDGET SETUP")
        print("=" * 60)
        print(f"Location: {self.user_location} ")

        budget_input = input("Max budget ($): ").strip()

        try:
            budget = int(budget_input.replace(',', '').replace('$', ''))
            if 50000 <= budget <= 2000000:
                self.user_budget = budget
                self.save_budget(budget)
                return True
            else:
                print("Budget must be $50,000 - $2,000,000")
        except ValueError:
            print("Invalid budget format")
        return False

    def search_properties(self):
        print("\n" + "=" * 60)
        print("                SEARCHING...")
        print("=" * 60)
        print(f"Location: {self.user_location}")
        print(f"Budget: ${self.user_budget:,}")
        print("Searching database...")

        try:
            response = requests.post(
                f"{self.service_url}/fetch-city-data",
                json={'city': self.current_city, 'state': self.current_state, 'limit': 100},
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    df = pd.read_csv(f"data/{data['filename']}")
                    filtered_df = df[df['price'] <= self.user_budget]
                    self.search_results = filtered_df.to_dict('records')
                    self.show_results()
                else:
                    print(f"Error: {data['error']}")
            else:
                print(f"Service error: {response.status_code}")

        except Exception as e:
            print(f"Error: {e}")

        input("Press Enter to continue...")

    def show_results(self):
        count = len(self.search_results)
        print(f"\nFound {count} homes under ${self.user_budget:,}")

        if count == 0:
            return

        # Show first 3 results
        for i, home in enumerate(self.search_results[:3], 1):
            print(f"\n{i}. {home.get('address', 'N/A')} - ${home.get('price', 0):,}")
            print(f"   {home.get('bedrooms', 0)} bed, {home.get('bathrooms', 0)} bath")
            print(f"   {home.get('square_footage', 0):,} sq ft")

        self.results_menu()

    def results_menu(self):
        while True:
            print("\n[S]ort [A]ll [V]save [N]ew [M]enu [Q]uit")
            choice = input("Choice: ").strip().upper()

            if choice == 'S':
                self.sort_results()
            elif choice == 'A':
                self.view_all()
            elif choice == 'V':
                self.save_results()
            elif choice == 'N':
                self.home_search()
                break
            elif choice == 'M':
                break
            elif choice == 'Q':
                self.quit_app()
            else:
                print("Invalid choice")

    def sort_results(self):
        print("\n[1] Price Low-High [2] Price High-Low [3] Size Large-Small")
        choice = input("Sort by: ").strip()

        if choice == '1':
            self.search_results.sort(key=lambda x: x.get('price', 0))
        elif choice == '2':
            self.search_results.sort(key=lambda x: x.get('price', 0), reverse=True)
        elif choice == '3':
            self.search_results.sort(key=lambda x: x.get('square_footage', 0), reverse=True)

        self.show_results()

    def view_all(self):
        print(f"\n{len(self.search_results)} Total Results:")
        for i, home in enumerate(self.search_results, 1):
            print(f"{i}. {home.get('address', 'N/A')} - ${home.get('price', 0):,}")
            if i % 10 == 0 and i < len(self.search_results):
                if input("Continue? (Enter/q): ").lower() == 'q':
                    break

    def save_results(self):
        filename = input("Filename (no extension): ").strip() or f"search_{datetime.now().strftime('%Y%m%d_%H%M')}"

        with open(f"{filename}.txt", 'w') as f:
            f.write(f"HOME SEARCH RESULTS\n")
            f.write(f"Location: {self.user_location}\n")
            f.write(f"Budget: ${self.user_budget:,}\n")
            f.write(f"Found: {len(self.search_results)} properties\n\n")

            for i, home in enumerate(self.search_results, 1):
                f.write(f"{i}. {home.get('address', 'N/A')} - ${home.get('price', 0):,}\n")
                f.write(f"   {home.get('bedrooms', 0)} bed, {home.get('bathrooms', 0)} bath\n\n")

        print(f"Saved to {filename}.txt")

    def show_help(self):
        print("\n" + "=" * 60)
        print("                    HELP")
        print("=" * 60)
        print("1. Enter city and 2-letter state code")
        print("2. Enter budget as whole number (no commas)")
        print("3. View and sort results")
        print("4. Save results to file")
        print("\nContact: valderrm@oregonstate.edu")
        input("Press Enter to continue...")

    def quit_app(self):
        # Clean up ZMQ connection
        if self.socket:
            try:
                self.socket.send_string("Q")  # Tell partner's service to quit
                self.socket.recv()
                self.socket.close()
            except:
                pass
        self.context.term()

        print("\nThank you for using HOME FINDER CLI!")
        print("Happy house hunting!")
        sys.exit(0)


def main():
    try:
        cli = HomeBuyerCLI()
        cli.display_welcome()
        cli.main_menu()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()