import requests

url = ('https://serpapi.com/search.json?engine=google_flights&'
       'departure_id=POZ&'
       'arrival_id=/m/02j9z&' # /m/02j9z code for EU
       'outbound_date=2024-10-24&'
       'return_date=2024-10-30&'
       'currency=EUR&hl=en&'
       'api_key=api_key')
response = requests.get(url)
print(response.json())
