import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from wit import Wit
from gtts import gTTS
import re

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot and Wit.ai tokens
BOT_TOKEN = '8187913138:AAHX0kQ_en1xSeBTP0g3g5uA-m8LtnbHKR8'
WIT_AI_TOKEN = 'KMWWCCHNJFFR2D3BF3QGI4SI7YR3FYOR'

# Initialize Wit.ai client
client = Wit(WIT_AI_TOKEN)

# Function to remove emojis and special characters for voice
def clean_text_for_voice(text):
    # Remove markdown links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove emojis and special characters
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text

# Convert text to speech with faster speed
def text_to_speech(response_text):
    # Clean text for voice
    clean_text = clean_text_for_voice(response_text)
    tts = gTTS(text=clean_text, lang='en', slow=False)
    audio_file = "response.mp3"
    tts.save(audio_file)
    return audio_file

# Reusable function to show home keyboard
def get_home_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Who am I?", callback_data='who_im_I')],
        [InlineKeyboardButton("My Projects", callback_data='projects')],
        [InlineKeyboardButton("Contact Me", callback_data='contact_me')],
        [InlineKeyboardButton("Voice/Text Settings", callback_data='settings')],
        [InlineKeyboardButton("Exit ❌", callback_data='exit')]
    ])

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Clear previous conversation history
    if 'messages' in context.user_data:
        del context.user_data['messages']
    
    # Initialize user preferences
    if 'voice_enabled' not in context.user_data:
        context.user_data['voice_enabled'] = True
    
    keyboard = get_home_keyboard()
    welcome_text = (
        "👋 Welcome! Type or say:\n\n"
        "'who' - Learn about Wallace\n"
        "'portfolio' - View portfolio\n"
        "'projects' - See projects\n"
        "'contact' - Get contact info\n"
        "'clear' - Start fresh\n"
        "'exit' - End session\n\n"
        "Or use the buttons below!"
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=keyboard)
        if context.user_data['voice_enabled']:
            audio_file = text_to_speech(welcome_text)
            await update.message.reply_voice(voice=open(audio_file, 'rb'))
    else:
        await update.callback_query.edit_message_text(text="🏠 Back to Home Menu:", reply_markup=keyboard)

# Button clicks
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    home_button = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Back to Home", callback_data='back')]])

    if query.data == 'settings':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Enable Voice", callback_data='enable_voice')],
            [InlineKeyboardButton("Disable Voice", callback_data='disable_voice')],
            [InlineKeyboardButton("Back to Home", callback_data='back')]
        ])
        await query.edit_message_text(
            text="🎛️ Voice/Text Settings:\nChoose your preferred response type:",
            reply_markup=keyboard
        )
    elif query.data == 'enable_voice':
        context.user_data['voice_enabled'] = True
        await query.edit_message_text(
            text="✅ Voice responses enabled!",
            reply_markup=home_button
        )
    elif query.data == 'disable_voice':
        context.user_data['voice_enabled'] = False
        await query.edit_message_text(
            text="✅ Voice responses disabled. You'll receive text-only responses.",
            reply_markup=home_button
        )
    elif query.data == 'who_im_I':
        await query.edit_message_text(
            text="🤖 I am Wallace, an AI enthusiast, bot and algorithm builder!\n\n"
                 "✅ Skilled in solving real-world problems with automation\n"
                 "✅ Team leader managing AI-based projects\n"
                 "✅ Experience in Blockchain, writing, project management and communication.\n"
                 "Let's innovate together! 🔥\n\n"
                 "Would you like to see my projects?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Yes", callback_data='projects')],
                [InlineKeyboardButton("No", callback_data='exit')]
            ])
        )
    elif query.data == 'projects':
        await query.edit_message_text(
            text="📂 My Projects:\n"
                 "🔹 HELB Bot - Assists with loan applications → [Try it](https://t.me/helbassit_bot) (Under Development)\n"
                 "🔹 AI Language Translator - Converts Kenyan dialects 🔁\n"
                 "🔹 Telegram Bots for clients 🤖\n"
                 "🔹 Voice-to-Text TTS projects 🎙️\n"
                 "🔹 Portfolio → [View](https://transcendent-tarsier-3c6ca6.netlify.app)\n"
                 "🔹 Healthcare Management System → [View](https://healthcare-management-system-iota.vercel.app/)\n"
                 "🔹 Recommender Algorithm (Under Development)\n"
                 "🔹 Kate Personal PC Assistant (Code on GitHub)\n\n"
                 "Would you like to go back to the home menu?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Yes", callback_data='back')],
                [InlineKeyboardButton("No", callback_data='exit')]
            ]),
            parse_mode='Markdown'
        )
    elif query.data == 'contact_me':
        await query.edit_message_text(
            text="📧 Contact me at: okekewallace@gmail.com\n"
                 "📱 Phone: 0707495340\n"
                 "🔗 LinkedIn: [Wallace Okeke](https://linkedin.com/in/wallaceokeke)\n"
                 "🔗 GitHub: [Wallace Okeke](https://github.com/wallaceokeke)\n"
                 "📱 WhatsApp: [Contact Me](https://wa.me/0757362321)\n\n"
                 "Click the WhatsApp link to start a conversation directly!",
            reply_markup=home_button,
            parse_mode='Markdown'
        )
    elif query.data == 'exit':
        await query.edit_message_text(
            text="👋 Thank you for visiting my portfolio bot!\nFeel free to /start again any time."
        )
    elif query.data == 'back':
        await start(update, context)

# Convert voice to text
def voice_to_text(file_path):
    with open(file_path, 'rb') as f:
        audio = f.read()
    response = client.speech(audio, {'Content-Type': 'audio/ogg'})
    if 'text' in response.get('entities', {}):
        return response['text']
    return "Sorry, I couldn't understand your voice."

# Handle voice messages
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.voice.get_file()
    await file.download_to_drive('voice.ogg')
    text = voice_to_text('voice.ogg')
    
    # Process voice commands
    if any(cmd in text.lower() for cmd in ['start', 'clear', 'exit', 'portfolio', 'projects', 'contact', 'who']):
        if 'clear' in text.lower():
            # Clear all history and state
            if 'messages' in context.user_data:
                del context.user_data['messages']
            if 'reminder_sent' in context.user_data:
                del context.user_data['reminder_sent']
            response_text = "🔄 Clearing conversation history..."
            await update.message.reply_text(response_text)
            await update.message.reply_text(
                "Fresh start! Type or say:\n"
                "'who' - About Wallace\n"
                "'portfolio' - View portfolio\n"
                "'projects' - See projects\n"
                "'contact' - Contact info"
            )
        else:
            response_text = f"Processing voice command: {text}"
            await update.message.reply_text(response_text)
            # Process the command as if it was typed
            await handle_text(update, context)
    else:
        response_text = f"I understood: {text}\n\nAvailable voice commands:\n- start\n- clear\n- exit\n- portfolio\n- projects\n- contact\n- who"
        await update.message.reply_text(response_text)
        if context.user_data.get('voice_enabled', True):
            audio_file = text_to_speech(response_text)
            await update.message.reply_voice(voice=open(audio_file, 'rb'))

# Handle regular text
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.lower()
    keyboard = get_home_keyboard()

    # Store message in history
    if 'messages' not in context.user_data:
        context.user_data['messages'] = []
    context.user_data['messages'].append(user_input)

    # Auto-clear history if too long
    if len(context.user_data['messages']) > 10:
        context.user_data['messages'] = context.user_data['messages'][-10:]

    # Command recognition
    if user_input in ['/start', 'start']:
        await start(update, context)
        return
    elif user_input in ['/exit', 'exit', 'quit', 'bye']:
        await update.message.reply_text(
            "👋 Goodbye! Type 'start' to begin again."
        )
        return
    elif user_input in ['/clear', 'clear']:
        # Clear all history and state
        if 'messages' in context.user_data:
            del context.user_data['messages']
        if 'reminder_sent' in context.user_data:
            del context.user_data['reminder_sent']
        await update.message.reply_text(
            "🔄 Fresh start! Type or say:\n"
            "'who' - About Wallace\n"
            "'portfolio' - View portfolio\n"
            "'projects' - See projects\n"
            "'contact' - Contact info",
            reply_markup=keyboard
        )
        return

    # Greeting recognition
    if any(greeting in user_input for greeting in ['hey', 'hi', 'hello', 'hola']):
        response = (
            "👋 Hi! Type:\n"
            "'who' - About Wallace\n"
            "'portfolio' - View portfolio\n"
            "'projects' - See projects\n"
            "'contact' - Contact info"
        )
    # Portfolio related
    elif 'portfolio' in user_input:
        response = "🔗 Portfolio: [View](https://transcendent-tarsier-3c6ca6.netlify.app)"
    # About Wallace
    elif any(word in user_input for word in ['who', 'about', 'wallace']):
        response = (
            "🤖 Wallace is an AI enthusiast, bot and algorithm builder!\n\n"
            "✅ Skilled in solving real-world problems with automation\n"
            "✅ Team leader managing AI-based projects\n"
            "✅ Experience in Blockchain, writing, project management and communication.\n\n"
            "Type 'projects' to see his work!"
        )
    # Projects related
    elif 'project' in user_input:
        response = (
            "📂 Projects:\n"
            "🔹 HELB Bot - Loan applications (Under Development)\n"
            "🔹 AI Language Translator - Kenyan dialects\n"
            "🔹 Telegram Bots for clients\n"
            "🔹 Voice-to-Text TTS projects\n"
            "🔹 Healthcare Management System\n"
            "🔹 Recommender Algorithm (Under Development)\n"
            "🔹 Kate Personal PC Assistant\n\n"
            "Type 'contact' to reach out!"
        )
    # Contact related
    elif 'contact' in user_input:
        response = (
            "📧 Contact:\n"
            "Email: okekewallace@gmail.com\n"
            "Phone: 0707495340\n"
            "LinkedIn: [Wallace Okeke](https://linkedin.com/in/wallaceokeke)\n"
            "GitHub: [Wallace Okeke](https://github.com/wallaceokeke)\n"
            "WhatsApp: [Contact Me](https://wa.me/0757362321)"
        )
    # Unrecognized input - first attempt
    elif not hasattr(context.user_data, 'reminder_sent'):
        response = (
            "Type:\n"
            "'who' - About Wallace\n"
            "'portfolio' - View portfolio\n"
            "'projects' - See projects\n"
            "'contact' - Contact info"
        )
        context.user_data.reminder_sent = True
    # Unrecognized input - second attempt
    else:
        response = (
            "Available commands:\n"
            "'who' - About Wallace\n"
            "'portfolio' - View portfolio\n"
            "'projects' - See projects\n"
            "'contact' - Contact info\n"
            "'clear' - Start fresh\n"
            "'exit' - End session"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Show Main Menu", callback_data='back')],
            [InlineKeyboardButton("Exit", callback_data='exit')]
        ])

    # Send text response
    await update.message.reply_text(
        response,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

    # Send voice response only if enabled
    if context.user_data.get('voice_enabled', True):
        audio_file = text_to_speech(response)
        await update.message.reply_voice(voice=open(audio_file, 'rb'))

# Run the bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.run_polling()

if __name__ == "__main__":
    main()
