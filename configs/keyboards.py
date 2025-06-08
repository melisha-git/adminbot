from telegram import Update, ReplyKeyboardMarkup, KeyboardButton

START_BUTTON = KeyboardButton('/start')
NEW_MESSAGE_BUTTON = KeyboardButton('/new_message')
STOP_BUTTON = KeyboardButton('/stop')

TYPES_BUTTON = KeyboardButton('/type')
MESSAGE_BUTTON = KeyboardButton('/message')
PREVIEW_BUTTON = KeyboardButton('/preview')
PUBLISH_BUTTON = KeyboardButton('/publish')

all_keyboard = [
    [START_BUTTON, NEW_MESSAGE_BUTTON, STOP_BUTTON]
]

start_keyboard = [
    [NEW_MESSAGE_BUTTON, STOP_BUTTON]
]

new_message_keyboard = [
    [TYPES_BUTTON, MESSAGE_BUTTON, PREVIEW_BUTTON, PUBLISH_BUTTON]
]

stop_keyboard = [
    [START_BUTTON]
]