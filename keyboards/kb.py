from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from middlewares.i18n import t
from config import WORKERS, TEMP_BOOSTS, PERM_BOOSTS


def main_menu(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Главное меню - только основные кнопки внизу экрана"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_main_menu", lang))],
        ],
        resize_keyboard=True
    )


def main_menu_buttons(lang: str = "ru") -> InlineKeyboardMarkup:
    """Все кнопки навигации внутри сообщения"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_profile", lang), callback_data="menu_profile"),
            InlineKeyboardButton(text=t("btn_deposit", lang), callback_data="menu_deposit"),
        ],
        [
            InlineKeyboardButton(text=t("btn_shop", lang), callback_data="menu_shop"),
            InlineKeyboardButton(text=t("btn_workers", lang), callback_data="menu_workers"),
        ],
        [
            InlineKeyboardButton(text=t("btn_farm", lang), callback_data="menu_farm"),
            InlineKeyboardButton(text=t("btn_boosts", lang), callback_data="menu_boosts"),
        ],
        [
            InlineKeyboardButton(text=t("btn_daily", lang), callback_data="menu_daily"),
            InlineKeyboardButton(text=t("btn_referral", lang), callback_data="menu_referral"),
        ],
        [
            InlineKeyboardButton(text=t("btn_withdraw", lang), callback_data="menu_withdraw"),
            InlineKeyboardButton(text=t("btn_stats", lang), callback_data="menu_stats"),
        ],
        [
            InlineKeyboardButton(text=t("btn_language", lang), callback_data="menu_language"),
        ],
    ])


def language_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора языка"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ],
        [InlineKeyboardButton(text="◀️ " + ("Назад" if "ru" else "Back"), callback_data="back_to_menu")],
    ])


def shop_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура магазина со всеми рабочими"""
    buttons = []
    for wid, wdata in WORKERS.items():
        name = wdata.get(f"name_{lang}", wdata["name_ru"])
        buttons.append([InlineKeyboardButton(
            text=f"{name} — {wdata['cost']} TON",
            callback_data=f"buy_worker_{wid}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ " + t("btn_back", lang), callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_buy_keyboard(worker_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура подтверждения покупки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ " + t("btn_confirm", lang), callback_data=f"confirm_buy_{worker_id}"),
            InlineKeyboardButton(text="❌ " + t("btn_cancel", lang), callback_data="back_to_shop"),
        ]
    ])


def workers_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура для управления рабочими"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 " + t("btn_collect", lang), callback_data="collect_income")],
        [InlineKeyboardButton(text="◀️ " + t("btn_back", lang), callback_data="back_to_menu")],
    ])


def farm_keyboard(can_upgrade: bool, cost: float, is_max: bool, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура фермы с кнопкой улучшения"""
    buttons = []
    if not is_max and can_upgrade:
        buttons.append([InlineKeyboardButton(
            text="⬆️ " + t("btn_upgrade_farm", lang, cost=cost),
            callback_data="upgrade_farm"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ " + t("btn_back", lang), callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def boosts_menu_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Главное меню бустов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ " + t("btn_temp_boosts", lang), callback_data="show_temp_boosts")],
        [InlineKeyboardButton(text="♾️ " + t("btn_perm_boosts", lang), callback_data="show_perm_boosts")],
        [InlineKeyboardButton(text="◀️ " + t("btn_back", lang), callback_data="back_to_menu")],
    ])


def temp_boosts_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура временных бустов"""
    buttons = []
    for key, data in TEMP_BOOSTS.items():
        name = data.get(f"name_{lang}", data["name_ru"])
        bonus_percent = int((data['multiplier'] - 1) * 100)
        buttons.append([InlineKeyboardButton(
            text=f"{name} — {data['cost']} TON (+{bonus_percent}%)",
            callback_data=f"buy_temp_{key}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ " + t("btn_back", lang), callback_data="back_to_boosts")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def perm_boosts_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура постоянных бустов"""
    buttons = []
    for key, data in PERM_BOOSTS.items():
        name = data.get(f"name_{lang}", data["name_ru"])
        bonus_percent = int(data['bonus'] * 100)
        buttons.append([InlineKeyboardButton(
            text=f"{name} — {data['cost']} TON (+{bonus_percent}%)",
            callback_data=f"buy_perm_{key}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ " + t("btn_back", lang), callback_data="back_to_boosts")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def withdraw_speed_keyboard(amount: float, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура выбора скорости вывода"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐢 " + t("speed_normal", lang), callback_data=f"wspeed_normal_{amount}")],
        [InlineKeyboardButton(text="🚀 " + t("speed_fast", lang), callback_data=f"wspeed_fast_{amount}")],
        [InlineKeyboardButton(text="⚡ " + t("speed_instant", lang), callback_data=f"wspeed_instant_{amount}")],
        [InlineKeyboardButton(text="❌ " + t("btn_cancel", lang), callback_data="back_to_menu")],
    ])


def withdraw_wallet_keyboard(amount: float, speed: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура выбора типа кошелька для вывода"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 TON", callback_data=f"wwallet_TON_{speed}_{amount}")],
        [InlineKeyboardButton(text="💵 USDT (TRC20)", callback_data=f"wwallet_USDT_{speed}_{amount}")],
        [InlineKeyboardButton(text="❌ " + t("btn_cancel", lang), callback_data="back_to_menu")],
    ])


def withdraw_confirm_keyboard(withdraw_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура подтверждения вывода"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ " + t("btn_confirm", lang), callback_data=f"wconfirm_{withdraw_id}"),
            InlineKeyboardButton(text="❌ " + t("btn_cancel", lang), callback_data="back_to_menu"),
        ]
    ])


def admin_withdraw_keyboard(withdraw_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для админа (одобрение/отклонение вывода)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"admin_approve_{withdraw_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_{withdraw_id}"),
        ]
    ])


def stats_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура для статистики"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 " + t("btn_top", lang), callback_data="show_top")],
        [InlineKeyboardButton(text="🏅 " + t("btn_achievements", lang), callback_data="show_achievements")],
        [InlineKeyboardButton(text="◀️ " + t("btn_back", lang), callback_data="back_to_menu")],
    ])


def admin_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура администратора"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 " + t("btn_admin_withdraws", lang), callback_data="admin_withdraws")],
        [InlineKeyboardButton(text="💰 " + t("btn_admin_balance", lang), callback_data="admin_add_balance")],
        [InlineKeyboardButton(text="📊 " + t("btn_admin_stats", lang), callback_data="admin_stats")],
        [InlineKeyboardButton(text="◀️ " + t("btn_back", lang), callback_data="back_to_menu")],
    ])


def profile_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура профиля пользователя"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 " + t("btn_deposit_history", lang), callback_data="deposit_history")],
        [InlineKeyboardButton(text="◀️ " + t("btn_back", lang), callback_data="back_to_menu")],
    ])


def deposit_keyboard(amount: float = 0, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура выбора суммы для пополнения"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 10 TON", callback_data="deposit_10")],
        [InlineKeyboardButton(text="💎 25 TON", callback_data="deposit_25")],
        [InlineKeyboardButton(text="💎 50 TON", callback_data="deposit_50")],
        [InlineKeyboardButton(text="💎 100 TON", callback_data="deposit_100")],
        [InlineKeyboardButton(text="💎 250 TON", callback_data="deposit_250")],
        [InlineKeyboardButton(text="💎 500 TON", callback_data="deposit_500")],
        [InlineKeyboardButton(text="💎 1000 TON", callback_data="deposit_1000")],
        [InlineKeyboardButton(
            text="✏️ " + ("Своя сумма" if lang == "ru" else "Custom amount"), 
            callback_data="deposit_custom"
        )],
        [InlineKeyboardButton(text="❌ " + t("btn_cancel", lang), callback_data="back_to_menu")],
    ])


def deposit_cancel_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура отмены пополнения"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ " + t("btn_cancel", lang), callback_data="back_to_menu")],
    ])


def deposit_check_keyboard(amount: float, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура для проверки оплаты"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔄 " + ("Проверить оплату" if lang == "ru" else "Check Payment"), 
            callback_data=f"check_deposit_{amount}"
        )],
        [InlineKeyboardButton(text="❌ " + ("Отмена" if lang == "ru" else "Cancel"), 
                              callback_data="back_to_menu")]
    ])


def back_to_menu_button(lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 " + t("btn_back", lang), callback_data="back_to_menu")]
    ])
