# Ask user to enter tracking numbers
tracking = input("Please enter your tracking number: ")

# Use tracking number to figure out delivery carrier
tracking_length = len(tracking)
# USPS (Domestic) - 22 length (usually), digit only
# International - 13 length
# UPS - 18 length
# DHL - 10 length, digit only
# FedEx - 12-14 length, digit only
carriers = [
    {"carrier": "USPS"},
    {"carrier": "UPS"},
    {"carrier": "DHL"},
    {"carrier": "FedEx"},
]

# Add tracking number to database(?)
