import logging
import os
from io import BytesIO
from collections import Counter
import math

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

user_images = {}

DEFAULT_COLORS = 6


def rgb_to_hex(r, g, b):
    return f"#{r:02X}{g:02X}{b:02X}"


def rgb_to_hsl(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2

    if max_c == min_c:
        h = s = 0.0
    else:
        d = max_c - min_c
        s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        if max_c == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_c == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6
    return int(h * 360), int(s * 100), int(l * 100)


def quantize_colors(img, num_colors):
    """Extract dominant colors using PIL quantize."""
    img_rgb = img.convert("RGB")
    # Resize for speed
    small = img_rgb.resize((150, 150), Image.LANCZOS)
    quantized = small.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
    quantized_rgb = quantized.convert("RGB")

    pixels = list(quantized_rgb.getdata())
    counter = Counter(pixels)
    total = len(pixels)

    colors = []
    for (r, g, b), count in counter.most_common(num_colors):
        pct = round((count / total) * 100, 1)
        colors.append((r, g, b, pct))
    return colors


def create_palette_image(colors):
    """Create a nice palette swatch image."""
    swatch_w = 120
    swatch_h = 80
    text_h = 60
    padding = 10
    cols = min(3, len(colors))
    rows = math.ceil(len(colors) / cols)

    total_w = cols * (swatch_w + padding) + padding
    total_h = rows * (swatch_h + text_h + padding) + padding + 40  # 40 for title

    img = Image.new("RGB", (total_w, total_h), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((padding, 10), "Colour Palette", fill=(220, 220, 220))

    for i, (r, g, b, pct) in enumerate(colors):
        col = i % cols
        row = i // cols
        x = padding + col * (swatch_w + padding)
        y = 40 + padding + row * (swatch_h + text_h + padding)

        # Swatch
        draw.rectangle([x, y, x + swatch_w, y + swatch_h], fill=(r, g, b))
        # Border
        draw.rectangle([x, y, x + swatch_w, y + swatch_h], outline=(200, 200, 200), width=1)

        # Text below swatch
        hex_code = rgb_to_hex(r, g, b)
        draw.text((x, y + swatch_h + 4), hex_code, fill=(220, 220, 220))
        draw.text((x, y + swatch_h + 20), f"rgb({r},{g},{b})", fill=(170, 170, 170))
        draw.text((x, y + swatch_h + 36), f"{pct}%", fill=(130, 200, 130))

    return img


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the *Colour Palette Extractor!*\n\n"
        "📤 Send me any image and I'll extract the dominant colours.\n\n"
        "For each colour you'll get:\n"
        "🎨 Visual swatch\n"
        "🔢 HEX code (e.g. #FF5733)\n"
        "📊 RGB values\n"
        "💡 HSL values\n"
        "📈 Percentage of the image\n\n"
        "Just send your image to get started!",
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *How to use:*\n\n"
        "1. Send any photo\n"
        "2. Choose how many colours to extract (3, 6, 8, or 12)\n"
        "3. Get a palette image + colour codes!\n\n"
        "Great for design inspiration, brand colours, and more.",
        parse_mode="Markdown",
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_bytes = await file.download_as_bytearray()
    user_images[user_id] = bytes(file_bytes)

    keyboard = [
        [
            InlineKeyboardButton("3 colours", callback_data="palette_3"),
            InlineKeyboardButton("6 colours", callback_data="palette_6"),
        ],
        [
            InlineKeyboardButton("8 colours", callback_data="palette_8"),
            InlineKeyboardButton("12 colours", callback_data="palette_12"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✅ Image received! How many colours do you want to extract?",
        reply_markup=reply_markup,
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    doc = update.message.document
    if not (doc.mime_type and doc.mime_type.startswith("image/")):
        await update.message.reply_text("❌ Please send an image file.")
        return

    file = await context.bot.get_file(doc.file_id)
    file_bytes = await file.download_as_bytearray()
    user_images[user_id] = bytes(file_bytes)

    keyboard = [
        [
            InlineKeyboardButton("3 colours", callback_data="palette_3"),
            InlineKeyboardButton("6 colours", callback_data="palette_6"),
        ],
        [
            InlineKeyboardButton("8 colours", callback_data="palette_8"),
            InlineKeyboardButton("12 colours", callback_data="palette_12"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✅ Image received! How many colours do you want to extract?",
        reply_markup=reply_markup,
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if user_id not in user_images:
        await query.message.reply_text("❌ No image found. Please send an image first.")
        return

    num_colors = int(query.data.split("_")[1])
    await query.message.reply_text("⏳ Extracting colours, please wait...")

    try:
        img = Image.open(BytesIO(user_images[user_id]))
        colors = quantize_colors(img, num_colors)

        # Build text report
        lines = [f"🎨 *Colour Palette — {num_colors} colours*\n"]
        for i, (r, g, b, pct) in enumerate(colors, 1):
            hex_code = rgb_to_hex(r, g, b)
            h, s, l = rgb_to_hsl(r, g, b)
            lines.append(
                f"*{i}.* `{hex_code}`\n"
                f"   RGB: `({r}, {g}, {b})`\n"
                f"   HSL: `({h}°, {s}%, {l}%)`\n"
                f"   Coverage: `{pct}%`\n"
            )

        text_report = "\n".join(lines)

        # Create palette image
        palette_img = create_palette_image(colors)
        output = BytesIO()
        palette_img.save(output, format="PNG")
        output.seek(0)

        await query.message.reply_photo(
            photo=output,
            caption=text_report,
            parse_mode="Markdown",
        )

    except Exception as e:
        logger.error(f"Palette extraction error: {e}")
        await query.message.reply_text(f"❌ Error extracting colours: {str(e)}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling an update:", exc_info=context.error)


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_error_handler(error_handler)
    logger.info("Colour Palette Bot started...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
