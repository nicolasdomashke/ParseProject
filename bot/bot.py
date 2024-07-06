import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from backend.backend import fetch_hh_data
from backend.backend import fetch_db_data
from backend.backend import export_vacancies_to_excel
import os

#filters = {'text': '', 'area': '1', 'per_page': '5', 'page': '0'}
#filters = {}
#region = "-"

REGIONS = {
    'москва': 1,
    'санкт-петербург': 2,
    'новосибирск': 4,
    'екатеринбург': 3,
    'нижний новгород': 66,
    'казань': 88,
    'челябинск': 104,
    'омск': 68,
    'самара': 78,
    'ростов-на-дону': 76,
    'уфа': 99,
    'красноярск': 54,
    'пермь': 72,
    'волгоград': 85,
    'владивосток': 105,
    'краснодар': 53,
}


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    context.user_data.setdefault('filters', {'area' : '-', 'employer' : '-'})
    update.message.reply_text(
        "/vacancies <...> для поиска нужной вакансии\n/export для сохранения результатов в excel таблицу\n/filter для настройки фильтров\n/updateDB для обновления базы данных"
    )

def update_database(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Обновление данных...")
    fetch_hh_data('vacancies')
    update.message.reply_text("Обновление завершено!")

def vacancies(update: Update, context: CallbackContext) -> None:
    #filters = {'text': '', 'area': '1'}
    context.user_data['page'] = 0
    query = ' '.join(context.args)
    context.user_data['filters']['text'] = query
    data = fetch_db_data(context.user_data['filters'])
    context.user_data['data'] = data
    if data:
        display_page(update, context)
    else:
        update.message.reply_text("Вакансии не найдены или возникла ошибка")

def set_filters(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton(f"Текущий регион: " + context.user_data['filters']['area'], callback_data='set_region')],
        [InlineKeyboardButton("Компания: " + context.user_data['filters']['employer'], callback_data='set_employer')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберете настройку:', reply_markup=reply_markup)

def display_page(update: Update, context: CallbackContext) -> None:
    page = context.user_data.get('page', 0)
    vacancies = context.user_data['data']
    items_per_page = 10
    start = page * items_per_page
    end = start + items_per_page
    results = vacancies[start:end]

    if results:
        message = ""
        for vacancy in results:
            message += (
                f"Вакансия: {vacancy.name}\n"
                f"Компания: {vacancy.employer_name}\n"
                f"Регион: {vacancy.area}\n"
                f"URL: {vacancy.url}\n"
                f"{'-'*40}\n"
            )
        keyboard = []
        if page > 0:
            keyboard.append(InlineKeyboardButton("Назад", callback_data='previous_page'))
        if end < len(vacancies):
            keyboard.append(InlineKeyboardButton("Вперед", callback_data='next_page'))
        reply_markup = InlineKeyboardMarkup([keyboard])

        if update.callback_query:
            update.callback_query.message.edit_text(message, reply_markup=reply_markup)
        else:
            update.message.reply_text(message, reply_markup=reply_markup)
    else:
        update.message.reply_text("Вакансии не найдены. Попробуйте изменить запрос или фильтры")

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
        query.edit_message_text(text="Введите название региона:\n(или '-' для сброса фильтра)")
        context.user_data['awaiting_region'] = True
    
    elif query.data == 'set_employer':
        query.edit_message_text(text="Введите название компании:\n(или '-' для сброса фильтра)")
        context.user_data['awaiting_employer'] = True

def filter_input(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('awaiting_region'):
        region_name = update.message.text.capitalize()
        if region_name.lower() in REGIONS:
            context.user_data['filters']['area'] = region_name
            update.message.reply_text(f"Установлен регион: {region_name}")
        elif region_name == "-":
            context.user_data['filters']['area'] = "-"
            update.message.reply_text(f"Фильтр сброшен")
        else:
            update.message.reply_text(f"Прошу прощения, я не знаю такого города (")
        context.user_data['awaiting_region'] = False
    elif context.user_data.get('awaiting_employer'):
        company_name = update.message.text.capitalize()
        if company_name == "-":
            context.user_data['filters']['employer'] = "-"
            update.message.reply_text(f"Фильтр сброшен")
        else:
            context.user_data['filters']['employer'] = company_name
            update.message.reply_text(f"Установлен фильтр по компании: {company_name}")
        context.user_data['awaiting_employer'] = False

def export(update: Update, context: CallbackContext) -> None:
    vacancies = context.user_data.get('data', [])
    if not vacancies:
        update.message.reply_text("Результы не найдены. Попробуйте /vacancies")
        return

    file_path = 'vacancies.xlsx'
    export_vacancies_to_excel(vacancies, file_path)

    with open(file_path, 'rb') as file:
        update.message.reply_document(file)
    os.remove(file_path)

def main() -> None:
    updater = Updater("")

    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("vacancies", vacancies))
    dispatcher.add_handler(CommandHandler("updateDB", update_database))
    dispatcher.add_handler(CommandHandler("filter", set_filters))
    dispatcher.add_handler(CommandHandler("export", export))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, filter_input))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
