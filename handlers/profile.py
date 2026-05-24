from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.db import get_user, get_referrals, get_user_deposits
from keyboards.kb import profile_keyboard
from utils.helpers import format_ton

router = Router()


async def show_profile_content(callback_or_message, user_id: int, lang: str, edit: bool = True):
    """Показывает профиль пользователя"""
    user = await get_user(user_id)
    deposits = await get_user_deposits(user_id, 5)
    ref_count = await get_referrals(user_id)
    
    if lang == "ru":
        text = (
            "╔══════════════════════╗\n"
            "║      👤 ПРОФИЛЬ      ║\n"
            "╚══════════════════════╝\n\n"
            f"👤 Имя: <b>{user['full_name']}</b>\n"
            f"🆔 ID: <code>{user_id}</code>\n\n"
            f"💰 Баланс: <b>{format_ton(user['balance'])} TON</b>\n"
            f"💎 Всего заработано: <b>{format_ton(user['total_earned'])} TON</b>\n"
            f"👷 Рабочих куплено: <b>{user['total_workers']}</b>\n"
            f"👥 Рефералов: <b>{ref_count}</b>\n"
            f"🌾 Уровень фермы: <b>{user['farm_level']}/10</b>\n"
            f"🔥 Серия входов: <b>{user['daily_streak']} дней</b>\n\n"
        )
        
        if deposits:
            text += "━━━━━━━━━━━━━━━━━━━━━━\n📜 <b>Последние пополнения:</b>\n"
            for d in deposits[:3]:
                text += f"  💰 +{d['amount']} TON — {d['created_at'][:10]}\n"
    else:
        text = (
            "╔══════════════════════╗\n"
            "║      👤 PROFILE      ║\n"
            "╚══════════════════════╝\n\n"
            f"👤 Name: <b>{user['full_name']}</b>\n"
            f"🆔 ID: <code>{user_id}</code>\n\n"
            f"💰 Balance: <b>{format_ton(user['balance'])} TON</b>\n"
            f"💎 Total earned: <b>{format_ton(user['total_earned'])} TON</b>\n"
            f"👷 Workers bought: <b>{user['total_workers']}</b>\n"
            f"👥 Referrals: <b>{ref_count}</b>\n"
            f"🌾 Farm level: <b>{user['farm_level']}/10</b>\n"
            f"🔥 Login streak: <b>{user['daily_streak']} days</b>\n\n"
        )
        
        if deposits:
            text += "━━━━━━━━━━━━━━━━━━━━━━\n📜 <b>Recent deposits:</b>\n"
            for d in deposits[:3]:
                text += f"  💰 +{d['amount']} TON — {d['created_at'][:10]}\n"
    
    if edit and hasattr(callback_or_message, 'message'):
        await callback_or_message.message.edit_text(text, reply_markup=profile_keyboard(lang), parse_mode="HTML")
    else:
        await callback_or_message.answer(text, reply_markup=profile_keyboard(lang), parse_mode="HTML")


@router.message(F.text.in_(["👤 Профиль", "👤 Profile"]))
async def show_profile(message: Message, lang: str):
    await show_profile_content(message, message.from_user.id, lang, edit=False)


async def show_profile_callback(callback: CallbackQuery, lang: str):
    await show_profile_content(callback, callback.from_user.id, lang, edit=True)
    await callback.answer()


@router.callback_query(F.data == "deposit_history")
async def deposit_history(callback: CallbackQuery, lang: str):
    deposits = await get_user_deposits(callback.from_user.id)
    
    if lang == "ru":
        if not deposits:
            text = "📜 <b>История пополнений пуста</b>\n\nПополните баланс через кнопку «💎 Пополнить」."
        else:
            text = "╔══════════════════════╗\n║  📜 ИСТОРИЯ ПОПОЛНЕНИЙ  ║\n╚══════════════════════╝\n\n"
            for d in deposits:
                status_emoji = "✅" if d['status'] == 'completed' else "⏳"
                text += f"{status_emoji} <b>{d['amount']} TON</b> — {d['created_at'][:16]}\n"
    else:
        if not deposits:
            text = "📜 <b>Deposit history is empty</b>\n\nDeposit via the «💎 Deposit」 button."
        else:
            text = "╔══════════════════════╗\n║  📜 DEPOSIT HISTORY   ║\n╚══════════════════════╝\n\n"
            for d in deposits:
                status_emoji = "✅" if d['status'] == 'completed' else "⏳"
                text += f"{status_emoji} <b>{d['amount']} TON</b> — {d['created_at'][:16]}\n"
    
    await callback.message.edit_text(text, reply_markup=profile_keyboard(lang), parse_mode="HTML")
    await callback.answer()
