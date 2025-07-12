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
        as well as some of the commands available to them!
        """
        print("*" * 75)
        print("Welcome to the Value Home Finder...CLI... \n ")
        print("This CLI will guide you throught the tedious process of finding affordable homes in your area!\n")
        print("Here are some commands available to you!")
        print("->  help - Show this help message")
        print("->  quit - Exit the program")
        print("*" * 75)

    def collect_user_location(self):
        """
        This function will collect and validate our user location via a microservice.
        """
        print("\n ---Location Information ---")

# test functions as we go :)
if __name__ =="__main__":
    cli = HomeBuyerCLI()
    cli.display_welcome()
    cli.collect_user_location()