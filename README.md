# Project Documentation: "Fitness Bot"  

## 1. Project Description  
This Telegram bot helps users improve their fitness and health by providing the following features:  
- BMI Calculation: Users can input their weight and height to calculate their Body Mass Index (BMI) and receive a classification (underweight, normal, overweight, or obese).  
- Reminders: Users can set reminders for workouts or other fitness-related activities at specific times, and the bot will send a notification.  
- Daily Fitness Challenges: The bot suggests random fitness challenges such as drinking water, doing push-ups, or walking a certain number of steps.  
- Food Photo Analysis: Users can send photos of their meals, and the bot can provide an estimated calorie count.  

## 2. Functionality  
- Calculate BMI: The user inputs their weight and height. The bot calculates BMI and categorizes it as underweight, normal, overweight, or obese.  
- Set Reminder: The bot sends workout reminders at the specified time.  
- Daily Challenge: The bot suggests a random fitness or healthy living challenge.  
- Your Challenges: Shows a list of the user’s active and completed challenges.  
- Food Photo: Analyzes a photo of food and provides an estimated calorie count (with potential external service integration).  
- Feedback: The /reviews command allows users to provide feedback about the bot.  

## 3. Usage  
### Getting Started  
- The /start command launches the bot and displays the menu:  
  - "Calculate BMI"  
  - "Set Reminder"  
  - "Daily Challenge"  
  - "Food Photo"  
  - "Your Challenges"  
  - "Feedback"  

### Example Scenario  
1. The user enters /start.  
2. Enters their name.  
3. Selects "Calculate BMI".  
4. Inputs weight and height.  
5. The bot calculates and returns the BMI and category.  

## 4. Technical Requirements  
- Language: Python.  
- Libraries:  
  - telebot for Telegram API.  
  - threading, datetime, time for reminders.  
  - json, os for managing user data and challenges.  

## 5. Command Examples  
- /start: Start interacting with the bot.  
- /reviews: Leave feedback. 
