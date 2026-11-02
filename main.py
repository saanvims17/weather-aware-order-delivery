
import asyncio
import json
import logging
import os
from pathlib import Path

import aiohttp
from dotenv import load_dotenv

# Project configuration
BASE_DIR = Path(__file__).resolve().parent
ORDERS_FILE = BASE_DIR / "orders.json"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

DELAY_WEATHER = {"Rain", "Snow", "Extreme"}

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)


def weather_aware_apology(customer, city, weather_main, description):
    """Generate a personalized weather-delay message."""

    first_name = customer.split()[0]

    if weather_main == "Rain":
        reason = f"rain ({description})"
    elif weather_main == "Snow":
        reason = f"snow ({description})"
    else:
        reason = f"extreme weather ({description})"

    return (
        f"Hi {first_name}, your order to {city} may be "
        f"delayed due to {reason}. "
        "We appreciate your patience and understanding!"
    )


async def fetch_weather(session, order, api_key):
    """Fetch weather for one order without stopping other requests."""

    city = order["city"]

    try:
        params = {
            "q": city,
            "appid": api_key,
        }

        async with session.get(WEATHER_URL, params=params) as response:
            try:
                data = await response.json(content_type=None)
            except (ValueError, aiohttp.ContentTypeError):
                raise RuntimeError("Invalid JSON from weather API")

            if not isinstance(data, dict):
                raise RuntimeError("Unexpected API response format")

            if response.status != 200:
                message = data.get("message", "Unknown API error")
                raise RuntimeError(
                    f"HTTP {response.status}: {message}"
                )

            weather = data.get("weather", [])

            if not isinstance(weather, list) or not weather:
                raise RuntimeError("Weather data missing from response")

            condition = weather[0].get("main")
            description = weather[0].get("description", condition)

            if not isinstance(condition, str) or not condition:
                raise RuntimeError("Weather condition missing")

            if not isinstance(description, str) or not description:
                description = condition

            logger.info("%s: %s (%s)", city, condition, description)

            return {
                "order_id": order["order_id"],
                "ok": True,
                "main": condition,
                "description": description,
            }

    except (
        aiohttp.ClientError,
        asyncio.TimeoutError,
        RuntimeError,
        ValueError,
    ) as error:
        logger.error(
            "Weather lookup failed for %s: %s",
            city,
            error,
        )

        return {
            "order_id": order["order_id"],
            "ok": False,
        }


async def main():
    # Load API key securely
    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")

    if not api_key:
        raise SystemExit("API key missing. Check your .env file.")

    # Read orders
    try:
        with ORDERS_FILE.open("r", encoding="utf-8") as file:
            orders = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"Could not read orders.json: {error}")

    if not isinstance(orders, list):
        raise SystemExit("Invalid orders.json: expected a list.")

    timeout = aiohttp.ClientTimeout(total=20)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        # Fetch all city weather concurrently
        results = await asyncio.gather(
            *[
                fetch_weather(session, order, api_key)
                for order in orders
            ]
        )

    result_by_id = {
        result["order_id"]: result
        for result in results
    }

    # Update order statuses
    for order in orders:
        result = result_by_id.get(order["order_id"])

        # Keep the existing order unchanged if lookup fails
        if not result or not result["ok"]:
            continue

        condition = result["main"]
        description = result["description"]

        if condition in DELAY_WEATHER:
            order["status"] = "Delayed"
            order["weather_main"] = condition
            order["delay_reason"] = description
            order["customer_message"] = weather_aware_apology(
                order["customer"],
                order["city"],
                condition,
                description,
            )
        else:
            # Assumes weather is the only reason for a delay
            order["status"] = "Pending"

            for key in (
                "weather_main",
                "delay_reason",
                "customer_message",
            ):
                order.pop(key, None)

    # Save updated orders
    try:
        with ORDERS_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                orders,
                file,
                indent=2,
                ensure_ascii=False,
            )
            file.write("\n")
    except OSError as error:
        raise SystemExit(f"Could not save orders.json: {error}")

    # Print delivery summary
    print("\n===== DELIVERY SUMMARY =====")

    for order in orders:
        print(
            f"Order {order['order_id']} | "
            f"{order['city']} | {order['status']}"
        )

        if "customer_message" in order:
            print(order["customer_message"])

    print("\nUpdated orders.json successfully.")


if __name__ == "__main__":
    asyncio.run(main())
