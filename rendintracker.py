import requests
import time
import json

#Add your discord webhook & role to ping here (@everyone, @rentfinders, etc., or by user ID)
webhook_url = "https://discordapp.com/api/webhooks/1124006826103545866/e_DDJMk59D4kWi9waeqL92LgR2RTBztCQQji-ZEVPrqV3VWa9Xt7Yti6qZ8B-SuvMUAy"
role_to_ping = "<@468349037394001921>"
max_price = 5000


def notify_discord_webhook(webhook_url, message):
    data = {
        'content': message
    }
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        print("Notification sent to Discord")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send notification: {e}")


def get_api_data(url, headers, body):
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()

        json_response = response.json()
        print("Response content:", json.dumps(json_response, indent=4))

        count = json_response['result']['count']
        last_apartment = json_response['result']['foundApartments'][0] if count > 0 else None

        return count, last_apartment
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None, None
    except (KeyError, TypeError):
        print(f"Invalid response format")
        return None, None


def main():

    print("main start")
    url = 'https://europe-west1-rendin-production.cloudfunctions.net/getSearchApartments'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0'} # Replace with your actual headers
    body = {"data":{"priceMax":max_price,"city":"Tallinn","districts":["Kesklinn"],"country":"EE"}} # Replace with your actual body
    
    notify_discord_webhook(webhook_url, f"Rendin scanner has started! Params: {body}")  # send notification to Discord

    prev_count, _ = get_api_data(url, headers, body)

    while True:
        time.sleep(600)  # Wait 10 minutes
        new_count, last_apartment = get_api_data(url, headers, body)
        #notify_discord_webhook(webhook_url, f"Count is: {new_count}, prev count is {prev_count}")  # send notification to Discord

        if new_count is None:
            continue

        if new_count > prev_count:  # notification only when count goes up
            message = f"{role_to_ping} New apartment found!\n"
            message += f"Link: {last_apartment['link']}\n"
            message += f"City: {last_apartment['city']}\n"
            message += f"Updated: {last_apartment['updated']}\n"
            message += f"Price: {last_apartment['price']} {last_apartment['currency']}\n"
            message += f"Object Area: {last_apartment['objectArea']} m2\n"
            message += f"Address: {last_apartment['address']}\n"

            print(message)
            notify_discord_webhook(webhook_url, message)  # send notification to Discord
        prev_count = new_count  # update prev_count after every API call


if __name__ == "__main__":
    main()
