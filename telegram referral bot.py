#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import random
import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for conversation handler
AMOUNT = 0

# Dictionary to store user data (in a real application, use a database)
user_data = {}
# Dictionary to track daily bonuses
daily_bonus_claimed = {}

# Constants
REFERRAL_REWARD = 15
MINIMUM_WITHDRAWAL = 150

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    user_id = user.id
    
    # Check if this is a referral
    if context.args and len(context.args) > 0:
        referrer_id = context.args[0]
        try:
            referrer_id = int(referrer_id)
            # Make sure the referrer exists and is not the same as the new user
            if referrer_id in user_data and referrer_id != user_id:
                # Credit the referrer
                user_data[referrer_id]["balance"] += REFERRAL_REWARD
                user_data[referrer_id]["referrals"] += 1
                logger.info(f"User {referrer_id} earned {REFERRAL_REWARD} from referral of {user_id}")
                
                # Notify the referrer
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=f"🎉 Congratulations! You earned {REFERRAL_REWARD} from a new referral!"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify referrer {referrer_id}: {e}")
        except ValueError:
            logger.warning(f"Invalid referral ID: {referrer_id}")
    
    # Initialize user data if not exists
    if user_id not in user_data:
        user_data[user_id] = {
            "balance": 0,
            "referrals": 0,
            "username": user.username or f"user{user_id}",
        }
    
    # Create referral link
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    
    welcome_message = (
        f"👋 Welcome, {user.first_name}!\n\n"
        f"This bot offers a referral-based earning system. Here's how it works:\n\n"
        f"• Earn {REFERRAL_REWARD} for each successful referral\n"
        f"• Claim a daily bonus once every 24 hours\n"
        f"• Withdraw your earnings when your balance exceeds {MINIMUM_WITHDRAWAL}\n\n"
        f"Use the buttons below to navigate:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("💰 Check Balance", callback_data="check_balance"),
            InlineKeyboardButton("🔗 My Referral Link", callback_data="referral_link"),
        ],
        [
            InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus"),
            InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"),
        ],
        [
            InlineKeyboardButton("ℹ️ How to Earn", callback_data="how_to_earn"),
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Initialize user data if not exists (in case they somehow bypassed /start)
    if user_id not in user_data:
        user_data[user_id] = {
            "balance": 0,
            "referrals": 0,
            "username": query.from_user.username or f"user{user_id}",
        }
    
    await query.answer()
    
    if query.data == "check_balance":
        balance_text = (
            f"💰 Your current balance: {user_data[user_id]['balance']}\n"
            f"👥 Total referrals: {user_data[user_id]['referrals']}\n\n"
            f"You need at least {MINIMUM_WITHDRAWAL} to withdraw."
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=balance_text, reply_markup=reply_markup)
    
    elif query.data == "referral_link":
        referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
        
        referral_text = (
            f"🔗 Share this link with your friends:\n\n"
            f"{referral_link}\n\n"
            f"You'll earn {REFERRAL_REWARD} for each person who joins using your link!"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=referral_text, reply_markup=reply_markup)
    
    elif query.data == "daily_bonus":
        today = datetime.datetime.now().date()
        last_claimed = daily_bonus_claimed.get(user_id)
        
        if last_claimed == today:
            bonus_text = "⚠️ You've already claimed your daily bonus today. Come back tomorrow!"
        else:
            # Random bonus between 5 and 20
            bonus_amount = random.randint(5, 20)
            user_data[user_id]["balance"] += bonus_amount
            daily_bonus_claimed[user_id] = today
            
            bonus_text = f"🎁 Congratulations! You received a daily bonus of {bonus_amount}!"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=bonus_text, reply_markup=reply_markup)
    
    elif query.data == "withdraw":
        balance = user_data[user_id]["balance"]
        
        if balance < MINIMUM_WITHDRAWAL:
            withdraw_text = (
                f"⚠️ Your current balance ({balance}) is below the minimum withdrawal amount.\n"
                f"You need at least {MINIMUM_WITHDRAWAL} to withdraw."
            )
            
            keyboard = [
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(text=withdraw_text, reply_markup=reply_markup)
        else:
            withdraw_text = (
                f"💸 You can withdraw your balance of {balance}.\n"
                f"Please enter the amount you want to withdraw:"
            )
            
            await query.edit_message_text(text=withdraw_text)
            return AMOUNT
    
    elif query.data == "how_to_earn":
        earn_text = (
            "💡 How to earn:\n\n"
            f"1️⃣ Refer friends - {REFERRAL_REWARD} per referral\n"
            "2️⃣ Claim daily bonus - Random amount between 5 and 20\n\n"
            f"You can withdraw once your balance reaches {MINIMUM_WITHDRAWAL}."
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=earn_text, reply_markup=reply_markup)
    
    elif query.data == "back_to_menu":
        # Recreate the main menu
        welcome_message = (
            f"👋 Welcome back, {query.from_user.first_name}!\n\n"
            f"This bot offers a referral-based earning system. Here's how it works:\n\n"
            f"• Earn {REFERRAL_REWARD} for each successful referral\n"
            f"• Claim a daily bonus once every 24 hours\n"
            f"• Withdraw your earnings when your balance exceeds {MINIMUM_WITHDRAWAL}\n\n"
            f"Use the buttons below to navigate:"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("💰 Check Balance", callback_data="check_balance"),
                InlineKeyboardButton("🔗 My Referral Link", callback_data="referral_link"),
            ],
            [
                InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus"),
                InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"),
            ],
            [
                InlineKeyboardButton("ℹ️ How to Earn", callback_data="how_to_earn"),
            ],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=welcome_message, reply_markup=reply_markup)
    
    return ConversationHandler.END

async def process_withdrawal_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the withdrawal amount entered by the user."""
    user_id = update.effective_user.id
    text = update.message.text
    
    try:
        amount = float(text)
        if amount <= 0:
            await update.message.reply_text(
                "⚠️ Please enter a positive amount.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
                ])
            )
            return ConversationHandler.END
        
        balance = user_data[user_id]["balance"]
        
        if amount > balance:
            await update.message.reply_text(
                f"⚠️ You cannot withdraw more than your balance ({balance}).",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
                ])
            )
            return ConversationHandler.END
        
        if amount < MINIMUM_WITHDRAWAL:
            await update.message.reply_text(
                f"⚠️ The minimum withdrawal amount is {MINIMUM_WITHDRAWAL}.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
                ])
            )
            return ConversationHandler.END
        
        # Process withdrawal (in a real app, this would involve payment processing)
        user_data[user_id]["balance"] -= amount
        
        await update.message.reply_text(
            f"✅ Withdrawal of {amount} processed successfully!\n"
            f"Your new balance is {user_data[user_id]['balance']}.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ])
        )
        
    except ValueError:
        await update.message.reply_text(
            "⚠️ Please enter a valid number.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ])
        )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel and end the conversation."""
    await update.message.reply_text(
        "Operation cancelled.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ])
    )
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "🤖 Bot Commands:\n\n"
        "/start - Start the bot and get the main menu\n"
        "/help - Show this help message\n"
        "/balance - Check your current balance\n"
        "/referral - Get your referral link\n"
        "/bonus - Claim your daily bonus\n"
        "/withdraw - Withdraw your earnings\n\n"
        "You can also use the inline buttons for easier navigation."
    )
    await update.message.reply_text(help_text)

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send balance information when the command /balance is issued."""
    user_id = update.effective_user.id
    
    if user_id not in user_data:
        user_data[user_id] = {
            "balance": 0,
            "referrals": 0,
            "username": update.effective_user.username or f"user{user_id}",
        }
    
    balance_text = (
        f"💰 Your current balance: {user_data[user_id]['balance']}\n"
        f"👥 Total referrals: {user_data[user_id]['referrals']}\n\n"
        f"You need at least {MINIMUM_WITHDRAWAL} to withdraw."
    )
    
    await update.message.reply_text(balance_text)

async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send referral link when the command /referral is issued."""
    user_id = update.effective_user.id
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    
    referral_text = (
        f"🔗 Share this link with your friends:\n\n"
        f"{referral_link}\n\n"
        f"You'll earn {REFERRAL_REWARD} for each person who joins using your link!"
    )
    
    await update.message.reply_text(referral_text)

async def bonus_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the daily bonus command."""
    user_id = update.effective_user.id
    
    if user_id not in user_data:
        user_data[user_id] = {
            "balance": 0,
            "referrals": 0,
            "username": update.effective_user.username or f"user{user_id}",
        }
    
    today = datetime.datetime.now().date()
    last_claimed = daily_bonus_claimed.get(user_id)
    
    if last_claimed == today:
        await update.message.reply_text("⚠️ You've already claimed your daily bonus today. Come back tomorrow!")
    else:
        # Random bonus between 5 and 20
        bonus_amount = random.randint(5, 20)
        user_data[user_id]["balance"] += bonus_amount
        daily_bonus_claimed[user_id] = today
        
        await update.message.reply_text(f"🎁 Congratulations! You received a daily bonus of {bonus_amount}!")

async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the withdraw command."""
    user_id = update.effective_user.id
    
    if user_id not in user_data:
        user_data[user_id] = {
            "balance": 0,
            "referrals": 0,
            "username": update.effective_user.username or f"user{user_id}",
        }
    
    balance = user_data[user_id]["balance"]
    
    if balance < MINIMUM_WITHDRAWAL:
        await update.message.reply_text(
            f"⚠️ Your current balance ({balance}) is below the minimum withdrawal amount.\n"
            f"You need at least {MINIMUM_WITHDRAWAL} to withdraw."
        )
    else:
        await update.message.reply_text(
            f"💸 You can withdraw your balance of {balance}.\n"
            f"Please enter the amount you want to withdraw:"
        )
        return AMOUNT
    
    return ConversationHandler.END

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")).build()

    # Add conversation handler for withdrawal
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("withdraw", withdraw_command),
            CallbackQueryHandler(button_callback, pattern="^withdraw$")
        ],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_withdrawal_amount)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("referral", referral_command))
    application.add_handler(CommandHandler("bonus", bonus_command))
    
    # Add conversation handler
    application.add_handler(conv_handler)
    
    # Add callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_callback))

    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    main() 
