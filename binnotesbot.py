import configs.config as config
import configs.keyboards as keyboards
import configs.types as ctypes
import message_state as message_state
import re
from deep_translator import GoogleTranslator
import yake

from telegram.constants import ParseMode
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    filters,
)

logger = config.logger

SELECT_TYPE, ENTER_MESSAGE = range(2)

ENTER_CHANNEL, ENTER_USERNAMES = range(2)

types = ctypes.TypeManager()

def restricted(func):
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        username = update.effective_user.username
        if config.MAIN_USERNAMES and username not in config.MAIN_USERNAMES:
            logger.warning(f'Пользователь {username} пытался получить доступ')
            await update.message.reply_text("❌ У вас нет доступа к этой команде.")
            return
        return await func(update, context)
    return wrapped

def restricted_config(func):
    async def wrapped_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if config.CHANNEL_ID is None or config.MAIN_USERNAMES is None:
            logger.warning(f'Не настроен config')
            await update.message.reply_text("❌ Настройте конфиг. Введите /start")
            return
        return await func(update, context)
    return wrapped_config

@restricted
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info('Обработка Start')
    
    types.__init__()
    
    await update.message.reply_text(
        f'Привет! Я - лучший админ-бот 2000 канала',
        reply_markup=ReplyKeyboardRemove(),
    )
    
    if config.CHANNEL_ID and config.MAIN_USERNAMES:
        await update.message.reply_text(
        f'У меня все данные о конфиге',
        reply_markup=ReplyKeyboardMarkup(keyboards.start_keyboard, resize_keyboard=True),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
        )
        
        return ConversationHandler.END
    
    await update.message.reply_text(
        f'У меня недостаточно данных о конфиге, укажи их',
        reply_markup=ReplyKeyboardRemove(),
    )
    
    await update.message.reply_text(
        f'Введите канал, который мне необходимо администировать',
        reply_markup=ReplyKeyboardRemove(),
    )
    
    logger.debug('Обработка Start завершена')
    
    return ENTER_CHANNEL

@restricted
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info('Обработка Stop')
    
    await update.message.reply_text(
        "Бот остановлен. До скорого!",
        reply_markup=ReplyKeyboardMarkup(keyboards.stop_keyboard, resize_keyboard=True),
        disable_web_page_preview=True
    )
    
    logger.debug('Обработка Stop завершена')

@restricted
@restricted_config
async def new_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info('Обработка New Message')
    
    if 'state' not in context.user_data:
        context.user_data['state'] = message_state.State()
    
    await update.message.reply_text(
        "Что настраиваем?",
        reply_markup=ReplyKeyboardMarkup(keyboards.new_message_keyboard, resize_keyboard=True),
        disable_web_page_preview=True
    )
    
    logger.debug('Обработка New Message завершена')

@restricted
@restricted_config
async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'state' not in context.user_data:
        context.user_data['state'] = message_state.State()
    
    user_state: message_state.State = context.user_data['state']
    
    text = ''
    
    if user_state.type is not None:
        text += f'<b>{types.type_to_string(user_state.type)}</b>\n\n'
    
    if user_state.message:
        text += f'{user_state.message}\n\n'
    
    if config.SIGN:
        text += f'{config.SIGN}\n\n'
    
    if user_state.tags:
        tags_text = ' '.join(f'#{tag}' for tag in user_state.tags)
        text += f'{tags_text}'
    
    await update.message.reply_text(
        f"Ваше сообщение:\n{text}",
        reply_markup=ReplyKeyboardMarkup(keyboards.new_message_keyboard, resize_keyboard=True),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

@restricted
@restricted_config
async def publish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'state' not in context.user_data:
        context.user_data['state'] = message_state.State()
    
    user_state: message_state.State = context.user_data['state']
    
    if user_state.type is None or user_state.message is None:
        logger.error('Сообщение пустое')
        return
    
    text = f'<b>{types.type_to_string(user_state.type)}</b>\n\n'
    text += f'{user_state.message}\n\n'
    
    if config.SIGN:
        text += f'{config.SIGN}\n\n'
    
    if user_state.tags:
        tags_text = ' '.join(f'#{tag}' for tag in user_state.tags)
        text += f'{tags_text}'
    
    await context.bot.send_message(
        chat_id=config.CHANNEL_ID,
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )
    
    await update.message.reply_text(
        f"Ваше сообщение успешно отправлено:\n",
        reply_markup=ReplyKeyboardMarkup(keyboards.start_keyboard, resize_keyboard=True),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

@restricted
@restricted_config
async def set_type_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = 'Выберите тип сообщения:\n'
    
    type_keyboard = [
        [KeyboardButton(types.type_to_string(t))]
        for t in types.get_types()
    ]
    
    for type in types.get_types():
        string_type = types.type_to_string(type)
        text += f'<b>{string_type}</b>\n'
    
    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(type_keyboard, resize_keyboard=True),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )
    
    return SELECT_TYPE

@restricted
@restricted_config
async def set_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Введите сообщение:',
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True
    )
    
    return ENTER_MESSAGE


@restricted
@restricted_config
async def type_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'state' not in context.user_data:
        context.user_data['state'] = message_state.State()

    user_state: message_state.State = context.user_data['state']
    
    chosen_type = types.string_to_type(update.message.text)
    if chosen_type is None:
        await update.message.reply_text("Не понимаю, выберите, пожалуйста, тип из списка.")
        return SELECT_TYPE
    
    user_state.type = chosen_type
    
    await update.message.reply_text(
        f"Тип обновлен\nЧто дальше?",
        reply_markup=ReplyKeyboardMarkup(keyboards.new_message_keyboard, resize_keyboard=True),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )
    
    return ConversationHandler.END

@restricted
@restricted_config
async def enter_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'state' not in context.user_data:
        context.user_data['state'] = message_state.State()
    
    user_state: message_state.State = context.user_data['state']
    
    user_state.message = update.message.text_html
    
    translated = GoogleTranslator(source='auto', target='en').translate(user_state.message)
    kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=5)
    keywords = kw_extractor.extract_keywords(translated)
    user_state.tags = [kw.replace(' ', '_').lower() for kw, _ in keywords]
    
    await update.message.reply_text(
        f"Сообщение обновлено\nЧто дальше?",
        reply_markup=ReplyKeyboardMarkup(keyboards.new_message_keyboard, resize_keyboard=True),
        disable_web_page_preview=True
    )
    
    return ConversationHandler.END

@restricted
async def enter_channel_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config.CHANNEL_ID = update.message.text_html
    
    await update.message.reply_text(
        'Теперь введите тех, у кого есть доступ к боту через пробел',
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True
    )
    
    return ENTER_USERNAMES

@restricted
async def enter_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_words = re.split(r'[,\s]+', update.message.text_html.strip())
    
    config.MAIN_USERNAMES = [re.sub(r'^[^a-zA-Zа-яА-ЯёЁ]+', '', word) for word in raw_words if word]
    
    await update.message.reply_text(
        'Вы успешно всё настроили',
        reply_markup=ReplyKeyboardMarkup(keyboards.start_keyboard, resize_keyboard=True),
        disable_web_page_preview=True
    )
    
    return ConversationHandler.END

@restricted
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменяю.")
    context.user_data['state'].default()
    return ConversationHandler.END

@restricted
async def cancel_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменяю.")
    config.CHANNEL_ID = None
    config.MAIN_USERNAMES = None
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    
    app.add_handler(CommandHandler('stop', stop_command))
    app.add_handler(CommandHandler('new_message', new_message_command))
    app.add_handler(CommandHandler('preview', preview))
    app.add_handler(CommandHandler('publish', publish))
    
    conv_start = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states= {
            ENTER_CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_channel_id)],
            ENTER_USERNAMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_usernames)]
        },
        fallbacks=[CommandHandler('cancel', cancel_setup)],
        allow_reentry=True,
    )
    
    conv_type = ConversationHandler(
        entry_points=[CommandHandler('type', set_type_command)],
        states= {
            SELECT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, type_chosen)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
    )
    
    conv_message = ConversationHandler(
        entry_points=[CommandHandler('message', set_message_command)],
        states= {
            ENTER_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_message)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
    )
    
    app.add_handler(conv_start)
    app.add_handler(conv_type)
    app.add_handler(conv_message)
    
    logger.info('Бот запущен!')
    app.run_polling()
