from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🖼 Create Photo Collage", callback_data="nav_start_collage")],
        [InlineKeyboardButton("📚 Project History", callback_data="nav_history"),
         InlineKeyboardButton("❓ Help Manual", callback_data="nav_help")]
    ]
    return InlineKeyboardMarkup(keyboard)

