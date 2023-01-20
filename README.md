# Google Reviews Scrapper
This application was built with Selenium and Selenium-Wire and can be used to scrape reviews from Google Maps.

# Usage
```python3 google_reviews_scraper.py 'Your search term'```

# Important: Selenium-Wire connection not secure
Selenium-Wire does not support https by default, for this you need to install a CA certificate in your browser. If you don't do this, the application may end up throwing a lot of errors regarding the certificate. Nevertheless, the program should still work with a little delay.
