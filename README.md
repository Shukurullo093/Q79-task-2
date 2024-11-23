# Quasar 79 Task Two. Telegram Bot with Aiogram 3

This repository contains a Telegram bot built using the Aiogram 3 framework. The bot utilizes several Python packages listed in the `requirements.txt` file.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7 or higher
- pip (Python package installer)

## Installation

Follow these steps to set up the bot on your local machine:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Shukurullo093/Q79-task-2.git
   cd your-repo-name
   
2. **Create a virtual environment (optional but recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   
3. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
   

4. **Set up your bot token:**

    Create a .env file in the root directory of your project and add your bot token and database link (I used Postgresql):

        BOT_TOKEN=your_bot_token_here
        DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/db_name
   
   Replace your_bot_token_here with the token you received from the BotFather.

## Notion

    create integration in https://www.notion.so/my-integrations page and get token
    create new page and database inside it, then find database id
    you need to create table columns with name and type as follows
    Title - title, URL - url, Category, Priority - rich_text, Created Time - created time

## Running the Bot

    To start the bot, run the following command:
        
        python3 tgbot/__main__.py

Make sure to replace main.py with the name of your main bot file if it's different.

## Usage

Once the bot is running, you can interact with it on Telegram. Use the commands you have implemented to test its functionality.

**Bot commands**
    
    /start - to start or refresh bot
    /settoken - to save Notion token

**Bot functionality**

    You can:
        1. save new link to Notion DB by click '🆕 Save new link 🔗' btn 
        2. view full list of saved links click 'List of Links' btn 
        3. create category click 'Categories' btn 
        4. get help click 'Help' btn 