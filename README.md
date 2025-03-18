# Telegram Referral Bot

A Telegram bot that offers a referral-based earning system, where users earn rewards for successful referrals.

## Features

- 💰 Earn 15 credits per successful referral
- 🎁 Claim a daily bonus (random amount between 5-20)
- 💸 Withdraw earnings when balance exceeds 150
- 📊 Track balance and referrals
- 🔗 Generate and share referral links
- 📱 User-friendly inline keyboard buttons

## Setup

1. **Prerequisites**
   - Python 3.7 or higher
   - A Telegram account
   - A Telegram Bot Token (obtained from [@BotFather](https://t.me/BotFather))

2. **Installation**
   ```bash
   # Clone the repository (if applicable)
   git clone <repository-url>
   cd telegram-referral-bot
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configuration**
   - Set your bot token as an environment variable:
     ```bash
     export TELEGRAM_BOT_TOKEN=""7684621636:AAGIYBY6HF1cRmM9xxOe55jwp_Mf_FqYnCc"
     ```
   - Alternatively, you can directly edit the token in the code:
     ```python
     # In telegram_referral_bot.py, find this line:
     application = Application.builder().token(os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")).build()
     # Replace "YOUR_BOT_TOKEN_HERE" with your actual token
     ```

4. **Running the Bot**
   ```bash
   python telegram_referral_bot.py
   ```

## Usage

1. **Start the Bot**
   - Send `/start` to the bot to get the welcome message and main menu

2. **Commands**
   - `/start` - Start the bot and get the main menu
   - `/help` - Show help message
   - `/balance` - Check your current balance
   - `/referral` - Get your referral link
   - `/bonus` - Claim your daily bonus
   - `/withdraw` - Withdraw your earnings

3. **Referral System**
   - Get your referral link from the main menu or by using the `/referral` command
   - Share the link with friends
   - When someone joins using your link, you earn 15 credits

4. **Daily Bonus**
   - Claim a random bonus (5-20 credits) once every 24 hours
   - Use the "Daily Bonus" button or the `/bonus` command

5. **Withdrawals**
   - You need a minimum balance of 150 to withdraw
   - Use the "Withdraw" button or the `/withdraw` command
   - Follow the prompts to complete the withdrawal

## Notes

- This is a demonstration bot with temporary in-memory storage
- In a production environment, you would want to:
  - Use a database for persistent storage
  - Implement actual payment processing for withdrawals
  - Add additional security measures
  - Deploy the bot to a server for 24/7 availability

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
