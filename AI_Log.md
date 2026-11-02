# AI Log — Weather-Aware Order Delivery System

## 1. Project Overview
Developed a Python application that retrieves current weather conditions for customer delivery locations and updates order statuses based on potentially disruptive weather.

## 2. AI Assistance
AI assistance was used to help structure the Python implementation, troubleshoot errors, and validate the application's behavior.

## 3. Implementation and Debugging

### Weather API Integration
- Integrated the OpenWeatherMap Current Weather API to retrieve weather information for delivery cities.
- Stored the API key in a `.env` file rather than hardcoding it in the source code.
- Used environment-variable loading to access the API key securely.

### Asynchronous Processing
- Used Python's asynchronous programming capabilities to fetch weather data for multiple cities concurrently.
- Handled unsuccessful API responses without terminating the application.

### Weather-Based Order Updates
- Configured the application to mark orders as `Delayed` when the main weather condition is `Rain`, `Snow`, or `Extreme`.
- Kept orders as `Pending` when the weather did not meet the delay criteria.
- Generated personalized apology messages for customers whose orders were delayed.

### Error Handling
- Tested an invalid city, `InvalidCity123`.
- Confirmed that the application logged the HTTP 404 error and continued processing the other orders.

### Testing and Validation
- Verified that the application could retrieve weather data for New York, Mumbai, and London.
- Observed London returning `Rain (light rain)` during testing.
- Confirmed that order 1003 was marked `Delayed` and that a personalized apology message was generated.
- Observed other valid cities returning cloudy conditions, leaving their orders `Pending`.

## 4. Challenges and Resolutions
- **Changing weather conditions:** Recognized that live API responses can differ between runs and that delay behavior depends on the returned weather.
- **Invalid city:** Implemented error handling so an invalid location does not crash the application.
- **Persistent results:** Verified that the application updates `orders.json` with order statuses and relevant delay information.

## 5. Final Outcome
The application integrates a live weather API with asynchronous processing, weather-based delivery decisions, personalized customer notifications, and invalid-location error handling.

## 6. Tools and Technologies
- Python
- asyncio
- aiohttp
- python-dotenv
- OpenWeatherMap API
- JSON
- AI-assisted development and debugging