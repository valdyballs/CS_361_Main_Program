import requests
import json
import sys

class HomeBuyerCLI:
    def __init__(self):
        self.user_location = None
        self.user_budget = None
        self.property_data = None

        # my ports yo (probably not these but i need tis for the commit)
        self.location_service_url = "http://localhost:5001"
        self.budget_service_url = "http://localhost:5002"
        self.rentcast_service_url = "http://localhost:5003"

    def display_welcome(self):

        """
        This function will great the user and give them a general guide of the program
        """
        print("Welcome to the Value Home Finder...ClI ")
        print("This CLI will guide you throught the tedious process of finding affordable homes in your area!")
