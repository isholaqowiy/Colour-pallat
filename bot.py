import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
import database
import handlers
from config import BOT_TOKEN

def main():
    # Construct a dedicated isolated asynchronous event loop runtime context mapping on boot initialization layers
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(database.init_db())

    if not BOT_TOKEN:
        print("Fatal error: Missing BOT_TOKEN structural deployment parameters variables mapping data values tracking strings.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    uploader_wizard = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.start_collage_flow, pattern="^nav_start_collage$")],
        states={
            handlers.UPLOADING_STAGE: [
                MessageHandler(filters.PHOTO, handlers.handle_photo_upload),
                CallbackQueryHandler(handlers.compile_collage_action, pattern="^action_compile_collage$")
            ]
        },
        fallbacks=[CommandHandler("start", handlers.start)]
    )

    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CallbackQueryHandler(handlers.menu_navigation_routing, pattern="^nav_"))
    app.add_handler(uploader_wizard)

    print("CollageGrid Engine Processing Hub Active & Polling live loop instances...")
    app.run_polling()

if __name__ == '__main__':
    main()

