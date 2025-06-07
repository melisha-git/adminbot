import logging

# Положить docker - secrets на VPS
BOT_TOKEN = '7583469448:AAFBpsi1p3vclTkZ0FjYTCENimy7ILfx7qg'
CHANNEL_ID = '@testtchki'
MAIN_USERNAME = {'melisssha'}

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)