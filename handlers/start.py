from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from database.db import get_user, create_user, update_balance, add_referral
from keyboards.kb import main_menu, main_menu_buttons
from middlewares.i18n import t
from utils.helpers import calculate_income, calculate_pending, format_ton
from config import REFERRAL_INVITE_BONUS

router = Router()


def build_main_text(user, income: float, pending: float, lang: str) -> str:
    bar_filled = min(int((pending / max(income, 0.001)) * 10), 10)
    bar = "🟩" * bar_filled + "⬜" * (10 - bar_filled)

    if lang == "ru":
        return (
            f"╔══════════════════════╗\n"
            f"║   🏭 WORKERS ON TON   ║\n"
            f"╚══════════════════════╝\n\n"
            f"👤 <b>{user['full_name']}</b>\n\n"
            f"💰 Баланс: <b>{format_ton(user['balance'])} TON</b>\n"
            f"📈 Доход/день: <b>{format_ton(income)} TON</b>\n"
            f"👷 Рабочих: <b>{user['total_workers']}</b>\n"
            f"🌾 Уровень фермы: <b>{user['farm_level']}/10</b>\n\n"
            f"⏳ Накоплено: <b>{format_ton(pending)} TON</b>\n"
            f"{bar}\n\n"
            f"💎 Всего заработано: <b>{format_ton(user['total_earned'])} TON</b>\n\n"
            f"👇 <b>Выберите действие:</b>"
        )
    else:
        return (
            f"╔══════════════════════╗\n"
            f"║   🏭 WORKERS ON TON   ║\n"
            f"╚══════════════════════╝\n\n"
            f"👤 <b>{user['full_name']}</b>\n\n"
            f"💰 Balance: <b>{format_ton(user['balance'])} TON</b>\n"
            f"📈 Income/day: <b>{format_ton(income)} TON</b>\n"
            f"👷 Workers: <b>{user['total_workers']}</b>\n"
            f"🌾 Farm level: <b>{user['farm_level']}/10</b>\n\n"
            f"⏳ Pending: <b>{format_ton(pending)} TON</b>\n"
            f"{bar}\n\n"
            f"💎 Total earned: <b>{format_ton(user['total_earned'])} TON</b>\n\n"
            f"👇 <b>Choose action:</b>"
        )


@router.message(CommandStart())
async def cmd_start(message: Message, lang: str):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name

    args = message.text.split()
    ref_id = None
    if len(args) > 1:
        try:
            ref_id = int(args[1])
            if ref_id == user_id:
                ref_id = None
        except ValueError:
            ref_id = None

    user = await get_user(user_id)
    is_new = user is None

    if is_new:
        await create_user(user_id, username, full_name, ref_id)
        if ref_id:
            ref_user = await get_user(ref_id)
            if ref_user:
                await update_balance(ref_id, REFERRAL_INVITE_BONUS)
                await add_referral(ref_id, user_id, 1)
                await message.answer(
                    f"🎉 <b>{'Бонус за реферала!' if lang == 'ru' else 'Referral bonus!'}</b>\n\n"
                    f"{'Вы пришли по реферальной ссылке!' if lang == 'ru' else 'You joined via referral link!'}\n"
                    f"💰 +<b>{REFERRAL_INVITE_BONUS} TON</b> {'зачислено!' if lang == 'ru' else 'added!'}",
                    parse_mode="HTML"
                )

    user = await get_user(user_id)
    income = await calculate_income(user_id)
    pending = await calculate_pending(user_id)

    greeting = (
        f"👋 {'Добро пожаловать' if lang == 'ru' else 'Welcome'}, <b>{full_name}</b>!\n\n"
        if is_new else ""
    )

    await message.answer(
        greeting + build_main_text(user, income, pending, lang),
        reply_markup=main_menu_buttons(lang),
        parse_mode="HTML"
    )
    
    await message.answer(
        "🏠 Главное меню" if lang == "ru" else "🏠 Main Menu",
        reply_markup=main_menu(lang)
    )


@router.message(F.text == "🏠 Главное меню")
@router.message(F.text == "🏠 Main Menu")
async def show_main_menu(message: Message, lang: str):
    user = await get_user(message.from_user.id)
    income = await calculate_income(message.from_user.id)
    pending = await calculate_pending(message.from_user.id)
    
    await message.answer(
        build_main_text(user, income, pending, lang),
        reply_markup=main_menu_buttons(lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, lang: str):
    user = await get_user(callback.from_user.id)
    income = await calculate_income(callback.from_user.id)
    pending = await calculate_pending(callback.from_user.id)
    
    await callback.message.edit_text(
        build_main_text(user, income, pending, lang),
        reply_markup=main_menu_buttons(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "menu_profile")
async def menu_profile(callback: CallbackQuery, lang: str):
    from handlers.profile import show_profile_callback
    await show_profile_callback(callback, lang)


@router.callback_query(F.data == "menu_deposit")
async def menu_deposit(callback: CallbackQuery, lang: str):
    from handlers.deposit import show_deposit_callback
    await show_deposit_callback(callback, lang)


@router.callback_query(F.data == "menu_shop")
async def menu_shop(callback: CallbackQuery, lang: str):
    from handlers.shop import show_shop_callback
    await show_shop_callback(callback, lang)


@router.callback_query(F.data == "menu_workers")
async def menu_workers(callback: CallbackQuery, lang: str):
    from handlers.workers import show_workers_callback
    await show_workers_callback(callback, lang)


@router.callback_query(F.data == "menu_farm")
async def menu_farm(callback: CallbackQuery, lang: str):
    from handlers.farm import show_farm_callback
    await show_farm_callback(callback, lang)


@router.callback_query(F.data == "menu_boosts")
async def menu_boosts(callback: CallbackQuery, lang: str):
    from handlers.boosts import show_boosts_callback
    await show_boosts_callback(callback, lang)


@router.callback_query(F.data == "menu_daily")
async def menu_daily(callback: CallbackQuery, lang: str):
    from handlers.daily import show_daily_callback
    await show_daily_callback(callback, lang)


@router.callback_query(F.data == "menu_referral")
async def menu_referral(callback: CallbackQuery, lang: str):
    from handlers.referral import show_referral_callback
    await show_referral_callback(callback, lang)


@router.callback_query(F.data == "menu_withdraw")
async def menu_withdraw(callback: CallbackQuery, lang: str):
    from handlers.withdraw import show_withdraw_callback
    await show_withdraw_callback(callback, lang)


@router.callback_query(F.data == "menu_stats")
async def menu_stats(callback: CallbackQuery, lang: str):
    from handlers.stats import show_stats_callback
    await show_stats_callback(callback, lang)


@router.callback_query(F.data == "menu_language")
async def menu_language(callback: CallbackQuery, lang: str):
    from handlers.language import show_language_callback
    await show_language_callback(callback, lang)
