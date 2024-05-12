## About the Project
Multilingual AI Trip Planner is a comprehensive travel planning application that allows users to plan their trips seamlessly by providing options for flights, trains, and hotels, along with information about tourism attractions at their destination. Users can customize their travel preferences and budget to tailor their trip according to their needs. The application supports multiple languages, ensuring accessibility to users worldwide

## Table of Contents
- [Tech Stack](#tech-stack)
- [Key Features](#key-features)
- [USP](#usp)
- [Process Flow Diagram](#process-flow-diagram)
- [Live & Demo](#live--demo)
- [Installation](#installation)
- [Business Model](#business-model)
- [Deployment](#deployment)
- [License](#license)

## Tech Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python (Flask framework)
- APIs: Kiwi, RailYatri, RapidAPI, Geoapify
- Webscraping for Translation
- Database: MongoDB
- Generative AI: Google Gemini Pro API

## Key Features
- <b>Trip Planning Assistant</b>: Helps users plan domestic trips in India.
  
- <b>Multilingual Support</b>:
  - The site offers multilingual support to cater to a wider audience in India.
  - This would involve translating the user interface and content into various Indian languages as well as Foreign Languages.
    
- <b>Customizable Itineraries</b>:
  - Users define source, destination, and departure date.
  - System checks for existing destination content in MongoDB.
  - If content is missing, uses Google Gemini Pro API to generate information on places to visit.
    
- <b>Travel & Accommodation Options</b>:
  - Integrates with web APIs to provide flight, train, and hotel options.
  - Users can choose based on their preferences.
    
- <b>Final Itinerary Page</b>:
  - Displays chosen flight, train, and hotel details.
  - Presents top places to visit at the destination with images.
    
- <b>Preference-based Planning</b>:
  - Users can specify comfort or budget preference besides basic details.
  - System tailors the final page based on this preference.

- <b>Preference-based Planning</b>:
  - Users can specify comfort or budget preference to tailor the final itinerary.

- <b>Trip Planning Assistant with Chatbot</b>:
  - Users interact with a chatbot to plan domestic trips in India.
  - Chatbot guides users through defining source, destination, departure date, and preference (comfort or budget).

## USP
**USP 1**: Multilingual Trip Planning: BharatBhraman breaks down language barriers! Plan your India trip confidently with our multilingual support for various regional and foreign languages.

**USP 2**: Dynamic & Customizable Itineraries:  India travel your way! BharatBhraman's dynamic planning lets you change your mind on the go.  Our flexible itineraries adapt to your preferences, ensuring a perfect trip.

**USP 3**: Transparent Planning, Zero Hidden Fees:  Plan your dream India trip without surprises. BharatBhraman provides comprehensive trip plans absolutely free, with no hidden fees or additional taxes. You only pay for what you book.

## Process Flow Diagram
**CUSTOMIZATION OPTION**
![QUICK_PICK.jpeg](..%2F..%2FDownloads%2FQUICK_PICK.jpeg)

**QUICK PICK OPTION**
![QUICK_PIC2.jpeg](..%2F..%2FDownloads%2FQUICK_PIC2.jpeg)

## Live & Demo
**Live**
https://bharatbhraman.biz/

**Youtube Video**
https://youtu.be/R1mTj2u-TDM

**ScreenShots**
![Screenshot 2024-05-12 at 11.51.00 AM.png](..%2FScreenshot%202024-05-12%20at%2011.51.00%E2%80%AFAM.png)
![Screenshot 2024-05-12 at 11.47.27 AM.png](..%2FScreenshot%202024-05-12%20at%2011.47.27%E2%80%AFAM.png)
![Screenshot 2024-05-12 at 11.47.15 AM.png](..%2FScreenshot%202024-05-12%20at%2011.47.15%E2%80%AFAM.png)
![Screenshot 2024-05-12 at 11.46.43 AM.png](..%2FScreenshot%202024-05-12%20at%2011.46.43%E2%80%AFAM.png)
![Screenshot 2024-05-12 at 11.40.48 AM.png](..%2FScreenshot%202024-05-12%20at%2011.40.48%E2%80%AFAM.png)
![Screenshot 2024-05-12 at 11.40.39 AM.png](..%2FScreenshot%202024-05-12%20at%2011.40.39%E2%80%AFAM.png)
![Screenshot 2024-05-12 at 11.40.00 AM.png](..%2FScreenshot%202024-05-12%20at%2011.40.00%E2%80%AFAM.png)
![Screenshot 2024-05-12 at 11.38.30 AM.png](..%2FScreenshot%202024-05-12%20at%2011.38.30%E2%80%AFAM.png)
![Screenshot 2024-05-12 at 11.37.52 AM.png](..%2FScreenshot%202024-05-12%20at%2011.37.52%E2%80%AFAM.png)
![Screenshot 2024-05-12 at 11.37.42 AM.png](..%2FScreenshot%202024-05-12%20at%2011.37.42%E2%80%AFAM.png)
![Screenshot 2024-05-12 at 11.37.22 AM.png](..%2FScreenshot%202024-05-12%20at%2011.37.22%E2%80%AFAM.png)
![Screenshot 2024-05-12 at 11.36.57 AM.png](..%2FScreenshot%202024-05-12%20at%2011.36.57%E2%80%AFAM.png)
![Screenshot 2024-05-12 at 11.36.36 AM.png](..%2FScreenshot%202024-05-12%20at%2011.36.36%E2%80%AFAM.png)

## Installation
Python Version >3.11
Install Dependencies to from `requirements.txt`
```
pip install -r /path/to/requirements.txt
```

Run app.py
```
python app.py
```

## Business Model
**Affiliate Links**: 
By incorporating affiliate links for flights, trains, and hotels, the Multilingual AI Trip Planner can generate revenue by earning a commission of 5% on the total cost of bookings made through these links. This model leverages partnerships with travel providers to monetize user bookings while providing a seamless booking experience for users.

**Guide Option**:
Offering guide services for historical monuments, museums, and other tourist attractions presents an opportunity to generate revenue. The platform can provide users with the option to hire local guides for personalized tours at specific destinations. By facilitating guide bookings, the platform can charge a commission of 10% on the fees paid by users to the guides. This model taps into the unorganized market of guide services and adds value to users by enhancing their travel experiences with expert guidance.

**Sponsored Content**: 
Offer sponsored content opportunities to travel-related businesses, such as airlines, hotels, and tour operators, to promote their services or destinations within the BharatBhraman platform.

**AdSense Integration**: 
Implement Google AdSense within BharatBhraman to display targeted advertisements to users based on their trip planning activities and preferences. AdSense can generate revenue through pay-per-click (PPC) or cost-per-thousand-impressions (CPM) models.

## Deployment
Using Render whole Repository can hosted.
Use Command Line
```
gunincorn app:app
```

## License
This project is [MIT](./LICENSE) licensed.
