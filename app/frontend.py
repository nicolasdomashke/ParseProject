import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from backend import fetch_hh_data
from backend import fetch_db_data

filters = {'text': '', 'area': '1', 'per_page': '5', 'page': '0'}
filters = {}

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Hi! I am your Job Search Bot. Use /vacancies to search for job vacancies."
    )

def update_database(update: Update, context: CallbackContext) -> None:
    fetch_hh_data('vacancies')
# Vacancies command handler
def vacancies(update: Update, context: CallbackContext) -> None:

    context.user_data['page'] = 0
    query = ' '.join(context.args)
    filters['text'] = query
    data = fetch_db_data(filters)
    context.user_data['data'] = data
    if data:
        display_page(update, context)
    else:
        update.message.reply_text("No vacancies found or an error occurred.")

def display_page(update: Update, context: CallbackContext) -> None:
    page = context.user_data.get('page', 0)
    vacancies = context.user_data['data']
    items_per_page = 10  # Number of items per page
    start = page * items_per_page
    end = start + items_per_page
    results = vacancies[start:end]

    if results:
        message = ""
        for vacancy in results:
            message += (
                f"Vacancy: {vacancy.name}\n"
                f"Employer: {vacancy.employer_name}\n"
                f"Area: {vacancy.area}\n"
                f"URL: {vacancy.url}\n"
                f"{'-'*40}\n"
            )
        keyboard = []
        if page > 0:
            keyboard.append(InlineKeyboardButton("Previous", callback_data='previous_page'))
        if end < len(vacancies):
            keyboard.append(InlineKeyboardButton("Next", callback_data='next_page'))
        reply_markup = InlineKeyboardMarkup([keyboard])

        if update.callback_query:
            update.callback_query.message.edit_text(message, reply_markup=reply_markup)
        else:
            update.message.reply_text(message, reply_markup=reply_markup)
    else:
        update.message.reply_text("No vacancies found.")

def set_filters(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Set Region", callback_data='set_region')],
        [InlineKeyboardButton("Set Job Category", callback_data='set_job_category')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Choose an option:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query.data == 'next_page':
        context.user_data['page'] += 1
        display_page(update, context)
    elif query.data == 'previous_page':
        context.user_data['page'] -= 1
        display_page(update, context)
    query.answer()
    
    if query.data == 'set_region':
        query.edit_message_text(text="Please enter the region code:")
        context.user_data['awaiting_region'] = True
    
    elif query.data == 'set_job_category':
        pass

def region_input(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('awaiting_region'):
        region_code = update.message.text
        filters['area'] = region_code
        update.message.reply_text(f"Region set to {region_code}.")
        context.user_data['awaiting_region'] = False

# Main function to start the bot
def main() -> None:
    # Replace 'YOUR_TOKEN' with your actual bot token
    updater = Updater("")


    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("vacancies", vacancies))
    dispatcher.add_handler(CommandHandler("updateDB", update_database))
    dispatcher.add_handler(CommandHandler("filter", set_filters))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, region_input))
    #dispatcher.add_handler(CallbackQueryHandler(handle_page, pattern='^next_page$'))
    #dispatcher.add_handler(CallbackQueryHandler(handle_page, pattern='^previous_page$'))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
