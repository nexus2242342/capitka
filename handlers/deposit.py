from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

from database.db import (
    get_user, update_balance, create_deposit_session, get_deposit_session,
    clear_deposit_session, create_deposit, get_user_deposits
)
from keyboards.kb import deposit_keyboard, deposit_cancel_keyboard, profile_keyboard
from utils.helpers import format_ton
from config import (
    DEPOSIT_MIN_AMOUNT, DEPOSIT_MAX_AMOUNT, TON_WALLET, USDT_WALLET, 
    SUPPORT_USERNAME, ADMIN_IDS
)

router = Router()


class DepositFSM(StatesGroup):
    waiting_custom_amount = State()


async def show_deposit_content(callback: CallbackQuery, lang: str, edit: bool = True):
    """Показывает начальный экран пополнения"""
    user = await get_user(callback.from_user.id)
    
    if lang == "ru":
        text = (
            "╔══════════════════════╗\n"
            "║    💎 ПОПОЛНЕНИЕ     ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Ваш баланс: <b>{format_ton(user['balance'])} TON</b>\n\n"
            "Выберите сумму для пополнения:\n"
            "💡 После выбора суммы вы получите инструкцию для оплаты."
        )
    else:
        text = (
            "╔══════════════════════╗\n"
            "║    💎 DEPOSIT        ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Your balance: <b>{format_ton(user['balance'])} TON</b>\n\n"
            "Choose deposit amount:\n"
            "💡 After selecting, you'll receive payment instructions."
        )
    
    if edit:
        await callback.message.edit_text(text, reply_markup=deposit_keyboard(0, lang), parse_mode="HTML")
    else:
        await callback.message.answer(text, reply_markup=deposit_keyboard(0, lang), parse_mode="HTML")
    await callback.answer()


async def show_deposit_callback(callback: CallbackQuery, lang: str):
    await show_deposit_content(callback, lang, edit=True)


@router.callback_query(F.data.startswith("deposit_"))
async def deposit_amount(callback: CallbackQuery, state: FSMContext, lang: str):
    data = callback.data
    
    if data == "deposit_custom":
        await state.set_state(DepositFSM.waiting_custom_amount)
        await callback.message.edit_text(
            "✏️ " + ("Введите сумму в TON:" if lang == "ru" else "Enter amount in TON:"),
            reply_markup=deposit_cancel_keyboard(lang),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    amount = int(data.split("_")[1])
    
    if amount < DEPOSIT_MIN_AMOUNT:
        await callback.answer(
            f"❌ {'Минимальная сумма' if lang == 'ru' else 'Minimum amount'}: {DEPOSIT_MIN_AMOUNT} TON",
            show_alert=True
        )
        return
    
    if amount > DEPOSIT_MAX_AMOUNT:
        await callback.answer(
            f"❌ {'Максимальная сумма' if lang == 'ru' else 'Maximum amount'}: {DEPOSIT_MAX_AMOUNT} TON",
            show_alert=True
        )
        return
    
    await show_deposit_instruction(callback.message, callback.from_user.id, amount, lang)
    await callback.answer()


@router.message(DepositFSM.waiting_custom_amount)
async def custom_amount(message: Message, state: FSMContext, lang: str):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer(
            "❌ " + ("Введите корректное число!" if lang == "ru" else "Enter a valid number!"),
            parse_mode="HTML"
        )
        return
    
    if amount < DEPOSIT_MIN_AMOUNT:
        await message.answer(
            f"❌ {'Минимальная сумма' if lang == 'ru' else 'Minimum amount'}: <b>{DEPOSIT_MIN_AMOUNT} TON</b>",
            parse_mode="HTML"
        )
        return
    
    if amount > DEPOSIT_MAX_AMOUNT:
        await message.answer(
            f"❌ {'Максимальная сумма' if lang == 'ru' else 'Maximum amount'}: <b>{DEPOSIT_MAX_AMOUNT} TON</b>",
            parse_mode="HTML"
        )
        return
    
    await state.clear()
    await show_deposit_instruction(message, message.from_user.id, amount, lang)


async def show_deposit_instruction(msg: Message, user_id: int, amount: float, lang: str):
    note = await create_deposit_session(user_id, amount)
    
    if lang == "ru":
        text = (
            "╔══════════════════════╗\n"
            "║    💎 ОПЛАТА         ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Сумма: <b>{amount} TON</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📤 <b>Отправьте перевод на один из кошельков:</b>\n\n"
            f"💎 TON:\n<code>{TON_WALLET}</code>\n\n"
            f"💵 USDT (TRC20):\n<code>{USDT_WALLET}</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📝 <b>ВАЖНО!</b>\n"
            "В комментарии/описании платежа укажите:\n"
            f"<code>{note}</code>\n\n"
            "❗ Без этого комментария бот не сможет зачислить средства!\n"
            "💰 Средства зачисляются автоматически в течение 1-5 минут после отправки.\n"
            f"📩 По вопросам: {SUPPORT_USERNAME}\n\n"
            "✅ <b>После отправки нажмите «Проверить оплату»</b>"
        )
    else:
        text = (
            "╔══════════════════════╗\n"
            "║    💎 PAYMENT       ║\n"
            "╚══════════════════════╝\n\n"
            f"💰 Amount: <b>{amount} TON</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📤 <b>Send payment to one of the wallets:</b>\n\n"
            f"💎 TON:\n<code>{TON_WALLET}</code>\n\n"
            f"💵 USDT (TRC20):\n<code>{USDT_WALLET}</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📝 <b>IMPORTANT!</b>\n"
            "In the payment comment, specify:\n"
            f"<code>{note}</code>\n\n"
            "❗ Without this comment, the bot cannot credit funds!\n"
            "💰 Funds are credited automatically within 1-5 minutes.\n"
            f"📩 Support: {SUPPORT_USERNAME}\n\n"
            "✅ <b>After sending, click «Check Payment»</b>"
        )
    
    check_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 " + ("Проверить оплату" if lang == "ru" else "Check Payment"), 
                              callback_data=f"check_deposit_{amount}")],
        [InlineKeyboardButton(text="❌ " + ("Отмена" if lang == "ru" else "Cancel"), 
                              callback_data="back_to_menu")]
    ])
    
    await msg.edit_text(text, reply_markup=check_button, parse_mode="HTML")


@router.callback_query(F.data.startswith("check_deposit_"))
async def check_deposit(callback: CallbackQuery, bot: Bot, lang: str):
    user_id = callback.from_user.id
    session = await get_deposit_session(user_id)
    
    if not session:
        await callback.answer(
            "❌ " + ("Сессия истекла. Начните пополнение заново." if lang == "ru" else "Session expired. Start deposit again."),
            show_alert=True
        )
        await callback.message.edit_text(
            "⏰ " + ("Время сессии истекло. Нажмите «Пополнить» заново." if lang == "ru" else "Session expired. Click «Deposit» again."),
            reply_markup=deposit_keyboard(0, lang),
            parse_mode="HTML"
        )
        return
    
    await callback.message.edit_text(
        "⏳ " + ("Проверка транзакций..." if lang == "ru" else "Checking transactions..."),
        parse_mode="HTML"
    )
    
    await asyncio.sleep(2)
    
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"confirm_deposit_{session['amount']}")],
        [InlineKeyboardButton(text="🔄 " + ("Проверить ещё раз" if lang == "ru" else "Check again"), 
                              callback_data=f"check_deposit_{session['amount']}")],
        [InlineKeyboardButton(text="❌ " + ("Отмена" if lang == "ru" else "Cancel"), 
                              callback_data="back_to_menu")]
    ])
    
    await callback.message.edit_text(
        "🔍 " + ("Транзакции не найдены.\n\nЕсли вы уже отправили платеж, нажмите «Я оплатил» для ручного подтверждения администратором." if lang == "ru" else "Transactions not found.\n\nIf you have already sent the payment, click «I paid» for manual confirmation by the administrator."),
        reply_markup=confirm_keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_deposit_"))
async def confirm_deposit(callback: CallbackQuery, bot: Bot, lang: str):
    user_id = callback.from_user.id
    amount = float(callback.data.split("_")[2])
    session = await get_deposit_session(user_id)
    
    if not session:
        await callback.answer(
            "❌ " + ("Сессия истекла. Начните пополнение заново." if lang == "ru" else "Session expired. Start deposit again."),
            show_alert=True
        )
        return
    
    admin_text = (
        f"💰 <b>Заявка на ручное пополнение!</b>\n\n"
        f"👤 Пользователь: {callback.from_user.full_name}\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"💎 Сумма: <b>{amount} TON</b>"
    )
    
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Зачислить", callback_data=f"admin_deposit_approve_{user_id}_{amount}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_deposit_reject_{user_id}"),
        ]
    ])
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text, reply_markup=confirm_keyboard, parse_mode="HTML")
        except Exception:
            pass
    
    if lang == "ru":
        await callback.message.edit_text(
            "✅ <b>Заявка отправлена!</b>\n\n"
            "Администратор проверит платеж и зачислит средства в ближайшее время.\n"
            f"Сумма: <b>{amount} TON</b>",
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            "✅ <b>Request sent!</b>\n\n"
            "The administrator will check the payment and credit the funds shortly.\n"
            f"Amount: <b>{amount} TON</b>",
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("admin_deposit_approve_"))
async def admin_approve_deposit(callback: CallbackQuery, bot: Bot, lang: str):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("No access", show_alert=True)
        return
    
    parts = callback.data.split("_")
    user_id = int(parts[3])
    amount = float(parts[4])
    
    session = await get_deposit_session(user_id)
    
    await update_balance(user_id, amount)
    if session:
        await create_deposit(user_id, amount, "MANUAL", f"manual_{user_id}")
        await clear_deposit_session(user_id)
    
    await callback.message.edit_text(
        f"✅ <b>Пополнение подтверждено!</b>\n\n"
        f"👤 Пользователю: <code>{user_id}</code>\n"
        f"💰 Зачислено: <b>{amount} TON</b>",
        parse_mode="HTML"
    )
    
    try:
        user = await get_user(user_id)
        await bot.send_message(
            user_id,
            f"✅ <b>Ваш баланс пополнен!</b>\n\n"
            f"💰 Зачислено: <b>{amount} TON</b>\n"
            f"💳 Новый баланс: <b>{format_ton(user['balance'])} TON</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass
    
    await callback.answer()


@router.callback_query(F.data.startswith("admin_deposit_reject_"))
async def admin_reject_deposit(callback: CallbackQuery, bot: Bot, lang: str):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("No access", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[3])
    session = await get_deposit_session(user_id)
    
    if session:
        await clear_deposit_session(user_id)
    
    await callback.message.edit_text(
        f"❌ <b>Пополнение отклонено!</b>\n\n"
        f"👤 Пользователь: <code>{user_id}</code>",
        parse_mode="HTML"
    )
    
    try:
        await bot.send_message(
            user_id,
            f"❌ <b>Ваша заявка на пополнение отклонена!</b>\n\n"
            f"📩 Обратитесь в поддержку: {SUPPORT_USERNAME}",
            parse_mode="HTML"
        )
    except Exception:
        pass
    
    await callback.answer()
