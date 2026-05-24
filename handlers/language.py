from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.db import set_user_language
from keyboards.kb import language_keyboard, main_menu_buttons

router = Router()


async def show_language_content(callback_or_message, lang: str, edit: bool = True):
    """Показывает выбор языка"""
    text = "🌍 <b>Выберите язык / Choose language:</b>"
    
    if edit and hasattr(callback_or_message, 'message'):
        await callback_or_message.message.edit_text(text, reply_markup=language_keyboard(), parse_mode="HTML")
    else:
        await callback_or_message.answer(text, reply_markup=language_keyboard(), parse_mode="HTML")


@router.message(F.text == "🌍 Язык / Language")
async def choose_language(message: Message, lang: str):
    await show_language_content(message, lang, edit=False)


async def show_language_callback(callback: CallbackQuery, lang: str):
    await show_language_content(callback, lang, edit=True)
    await callback.answer()


@router.callback_query(F.data == "lang_ru")
async def set_ru(callback: CallbackQuery):
    await set_user_language(callback.from_user.id, "ru")
    await callback.message.edit_text("✅ <b>Язык изменён на Русский!</b>", parse_mode="HTML")
    
    from handlers.start import build_main_text
    from database.db import get_user
    from utils.helpers import calculate_income, calculate_pending
    
    user = await get_user(callback.from_user.id)
    income = await calculate_income(callback.from_user.id)
    pending = await calculate_pending(callback.from_user.id)
    
    await callback.message.answer(
        build_main_text(user, income, pending, "ru"),
        reply_markup=main_menu_buttons("ru"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "lang_en")
async def set_en(callback: CallbackQuery):
    await set_user_language(callback.from_user.id, "en")
    await callback.message.edit_text("✅ <b>Language changed to English!</b>", parse_mode="HTML")
    
    from handlers.start import build_main_text
    from database.db import get_user
    from utils.helpers import calculate_income, calculate_pending
    
    user = await get_user(callback.from_user.id)
    income = await calculate_income(callback.from_user.id)
    pending = await calculate_pending(callback.from_user.id)
    
    await callback.message.answer(
        build_main_text(user, income, pending, "en"),
        reply_markup=main_menu_buttons("en"),
        parse_mode="HTML"
    )
    await callback.answer()
