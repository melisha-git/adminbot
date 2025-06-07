import configs.config as config
import configs.keyboards as keyboards
import configs.types as types
import message_state as message_state
import re

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

MAIN_MENU, SELECT_TYPE, ENTER_MESSAGE, ENTER_TAGS = range(4)

def restricted(func):
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        username = update.effective_user.username
        if username not in config.MAIN_USERNAME:
            logger.warning(f'Пользователь {username} пытался получить доступ')
            await update.message.reply_text("❌ У вас нет доступа к этой команде.")
            return
        return await func(update, context)
    return wrapped

@restricted
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info('Обработка Start')
    
    await update.message.reply_text(
        f'Привет! Я - админ - бот канала {config.CHANNEL_ID}',
        reply_markup=ReplyKeyboardMarkup(keyboards.start_keyboard, resize_keyboard=True),
        disable_web_page_preview=True
    )
    
    logger.debug('Обработка Start завершена')

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
async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'state' not in context.user_data:
        context.user_data['state'] = message_state.State()
        
    user_state: message_state.State = context.user_data['state']
    
    text = ''
    
    if user_state.type:
        text += f'<b>{types.type_to_string(user_state.type)}</b>\n\n'
    
    if user_state.message:
        text += f'{user_state.message}\n\n'
    
    text += 'Segmentation fault (core dumped)\n\n'
    
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
async def publish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'state' not in context.user_data:
        context.user_data['state'] = message_state.State()
    
    user_state: message_state.State = context.user_data['state']
    
    if user_state.type is None or user_state.message is None:
        logger.error('Сообщение пустое')
        return
    
    text = f'<b>{types.type_to_string(user_state.type)}</b>\n\n'
    text += f'{user_state.message}\n\n'
    text += 'Segmentation fault (core dumped)\n\n'
    
    if user_state.tags:
        tags_text = ' '.join(f'#{tag}' for tag in user_state.tags)
        text += f'{tags_text}'
    
    await context.bot.send_message(
        chat_id=config.CHANNEL_ID,
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

@restricted
async def set_type_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = 'Выберите тип сообщения:\n'
    
    type_keyboard = [
        [KeyboardButton(types.type_to_string(t))]
        for t in types.Types
    ]
    
    for type in types.Types:
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
async def set_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Введите сообщение:',
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True
    )
    
    return ENTER_MESSAGE

@restricted
async def set_tags_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Введите теги:',
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True
    )
    
    return ENTER_TAGS


@restricted
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
    
    return MAIN_MENU

@restricted
async def enter_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'state' not in context.user_data:
        context.user_data['state'] = message_state.State()
    
    user_state: message_state.State = context.user_data['state']
    
    user_state.message = update.message.text_html
    
    await update.message.reply_text(
        f"Сообщение обновлено\nЧто дальше?",
        reply_markup=ReplyKeyboardMarkup(keyboards.new_message_keyboard, resize_keyboard=True),
        disable_web_page_preview=True
    )
    
    return MAIN_MENU

@restricted
async def enter_tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'state' not in context.user_data:
        context.user_data['state'] = message_state.State()

    user_state: message_state.State = context.user_data['state']
    
    raw_words = re.split(r'[,\s]+', update.message.text_html.strip())
    
    user_state.tags = [re.sub(r'^[^a-zA-Zа-яА-ЯёЁ]+', '', word) for word in raw_words if word]
    
    await update.message.reply_text(
        f"Теги обновлены\nЧто дальше?",
        reply_markup=ReplyKeyboardMarkup(keyboards.new_message_keyboard, resize_keyboard=True),
        disable_web_page_preview=True
    )
    
    return MAIN_MENU

@restricted
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменяю.")
    context.user_data['state'].default()
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('stop', stop_command))
    app.add_handler(CommandHandler('new_message', new_message_command))
    app.add_handler(CommandHandler('preview', preview))
    app.add_handler(CommandHandler('publish', publish))
    
    conv_type = ConversationHandler(
        entry_points=[CommandHandler('set_type', set_type_command)],
        states= {
            MAIN_MENU: [CommandHandler('new_message', new_message_command)],
            SELECT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, type_chosen)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
    )
    
    conv_message = ConversationHandler(
        entry_points=[CommandHandler('set_message', set_message_command)],
        states= {
            MAIN_MENU: [CommandHandler('new_message', new_message_command)],
            ENTER_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_message)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
    )
    
    conv_tags = ConversationHandler(
        entry_points=[CommandHandler('set_tags', set_tags_command)],
        states= {
            MAIN_MENU: [CommandHandler('new_message', new_message_command)],
            ENTER_TAGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_tags)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
    )
    
    app.add_handler(conv_type)
    app.add_handler(conv_message)
    app.add_handler(conv_tags)
    
    logger.info('Бот запущен!')
    app.run_polling()
