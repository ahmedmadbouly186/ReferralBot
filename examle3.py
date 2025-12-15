import requests
from bs4 import BeautifulSoup

def count_custom_span(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP requests

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        spans = soup.find_all('div',attrs={'class':'NativeElement ng-star-inserted','data-margin-bottom':"large"} )
        for span in spans:
            print(span.text.strip())
        # Count the number of matching elements
        count = len(spans)
        print(f"Number of elements: {count}")
        return count

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return 0

# Example usage
url = "https://www.freelancer.com/u/AwaisChaudhry"  # Replace with the target URL
count_custom_span(url)
