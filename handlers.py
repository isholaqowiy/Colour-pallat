import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
import database
import collage_generator
import utils
import keyboards
from config import TEMP_DIR

UPLOADING_STAGE = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utils.ensure_temp_directory()
    uid = update.effective_user.id
    await database.register_user(uid)
    
    welcome = (
        "👋 Welcome to *CollageGrid Bot*!\n"
        "Create stunning photo collages in just a few taps.\n\n"
        "🖼 *Combine 2–20 photos into beautiful layouts*\n"
        "📐 *Choose from professional grid templates*\n"
        "🎨 *Borders, background composition, and spacing alignment parameters*\n\n"
        "Upload your photos or choose an option below to get started."
    )
    if update.message:
        await update.message.reply_text(welcome, reply_markup=keyboards.get_main_menu(), parse_mode="Markdown")
    return ConversationHandler.END

async def start_collage_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["uploaded_images"] = []
    
    kb = [[InlineKeyboardButton("✅ Done Uploading - Generate!", callback_data="action_compile_collage")]]
    await query.message.reply_text("📥 Please upload between *2 to 20 Photos* one after another. Tap the button below when your batch upload is completed:", 
                                   reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    return UPLOADING_STAGE

async def handle_photo_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    photo = update.message.photo[-1]
    
    if "uploaded_images" not in context.user_data:
        context.user_data["uploaded_images"] = []
        
    img_count = len(context.user_data["uploaded_images"])
    if img_count >= 20:
        await update.message.reply_text("⚠️ Maximum upload limits threshold boundary crossed. You cannot add more than 20 images to one collage batch sequence.")
        return UPLOADING_STAGE
        
    tg_file = await context.bot.get_file(photo.file_id)
    target_filename = os.path.join(TEMP_DIR, f"raw_{uid}_{img_count}.png")
    await tg_file.download_to_drive(target_filename)
    
    context.user_data["uploaded_images"].append(target_filename)
    await update.message.reply_text(f"📥 Received photo {len(context.user_data['uploaded_images'])}/20. Continue uploading or tap 'Done Uploading'.")
    return UPLOADING_STAGE

async def compile_collage_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    
    image_list = context.user_data.get("uploaded_images", [])
    if len(image_list) < 2:
        await query.message.reply_text("⚠️ Insufficient assets. Please upload at least 2 photos before attempting compilation.")
        return UPLOADING_STAGE
        
    await query.message.reply_text("⚡ Processing, scaling, and stitching your photo collage grid layout vectors...")
    
    output_file = collage_generator.build_collage(image_list, uid)
    if output_file and os.path.exists(output_file):
        with open(output_file, "rb") as f:
            await query.message.reply_photo(photo=f, caption="✨ Grid composition rendering complete! Processed via CollageGrid Engine layers.")
        await database.save_collage_log(uid, len(image_list), "Standard Grid")
        utils.clean_user_files(uid)
    else:
        await query.message.reply_text("❌ An error occurred while computing the image grid rendering dimensions bounds.")
        
    return ConversationHandler.END

async def menu_navigation_routing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    
    if query.data == "nav_history":
        history = await database.get_user_history(uid)
        if not history:
            await query.message.reply_text("📂 No historical collage records traced inside your database logs index yet.", reply_markup=keyboards.get_main_menu())
        else:
            msg = "📂 *Your Recent Photo Grid Collages History Logs:*\n\n" + "\n".join([f"- Stitched `{item['count']}` images inside a `{item['style']}` matrix." for item in history])
            await query.message.reply_text(msg, reply_markup=keyboards.get_main_menu(), parse_mode="Markdown")
    elif query.data == "nav_help":
        help_text = (
            "❓ *CollageGrid Core Engine Manual*\n\n"
            "This bot leverages programmatic matrix scaling routines to distribute "
            "irregular raw dimensions layouts onto uniform print boundaries safely.\n\n"
            "💡 *Usage:* Click 'Create Photo Collage', batch-upload your image file paths, and export high-resolution frames directly."
        )
        await query.message.reply_text(help_text, reply_markup=keyboards.get_main_menu(), parse_mode="Markdown")

