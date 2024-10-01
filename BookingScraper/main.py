import pandas as pd
from playwright.sync_api import sync_playwright
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    logging.debug("Starting the script...")

    with sync_playwright() as p:
        checkin_date = '2025-03-23'
        checkout_date = '2025-03-24'
        url = f'https://www.booking.com/searchresults.en-us.html?checkin={checkin_date}&checkout={checkout_date}&selected_currency=USD&ss=Paris&ssne=Paris&ssne_untouched=Paris&lang=en-us&sb=1&src_elem=sb&src=searchresults&dest_type=city&group_adults=1&no_rooms=1&group_children=0&sb_travel_purpose=leisure'

        logging.debug(f"Navigating to URL: {url}")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        logging.debug("Page loaded successfully.")

        hotels = page.locator('[data-testid="property-card"]').all()
        logging.info(f'There are: {len(hotels)} hotels for your request.')

        hotels_list = []
        for hotel in hotels:
            hotel_dict = {
                'hotel': hotel.locator('//div[@data-testid="title"]').inner_text(),
                'price': hotel.locator('//span[@data-testid="price-and-discounted-price"]').inner_text(),
                'score': hotel.locator('//div[@data-testid="review-score"]/div[1]').inner_text(),
                'avg review': hotel.locator('//div[@data-testid="review-score"]/div[2]/div[1]').inner_text(),
                'reviews count': hotel.locator('//div[@data-testid="review-score"]/div[2]/div[2]').inner_text().split()[
                    0]
            }
            logging.debug(f"Extracted hotel data: {hotel_dict}")
            hotels_list.append(hotel_dict)

        df = pd.DataFrame(hotels_list)
        df.to_excel('hotels_list.xlsx', index=False)
        logging.info("Saved data to Excel.")
        df.to_csv('hotels_list.csv', index=False)
        logging.info("Saved data to CSV.")

        browser.close()
        logging.debug("Browser closed.")


if __name__ == '__main__':
    main()
