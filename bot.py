import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================================================================
# ✏️  ВСЕ ТЕКСТЫ КВЕСТА — РЕДАКТИРУЙ ЗДЕСЬ
# ================================================================

# Пароль для команд /skip и /restart (можешь поменять)
ADMIN_PASSWORD = "черкас"

# --- Вступление ---
INTRO_TEXT = """
☠️ Кхе-кхе... Значит, явились, морские крысы.

Я — дух капитана Черкаса, которого собственный мушкет уложил у слияния рек. Обидно, блядь. Но перед тем как отправиться к морскому дьяволу, я спрятал кое-что ценное в этих водах.

Вас семеро — пройдите шесть испытаний. Каждое откроет часть моего последнего письма. Сложите всё вместе — узнаете, где моё сокровище.

Якорь вам в задницу, если облажаетесь.

Начните у Первой Преграды. ⚓
"""

# --- Подсказка куда плыть перед точкой 1 (отправляется по /start) ---
START_HINT = "🗺 Снимайте швартовы! Курс на Первую Преграду — плывите к дамбе на реке!"

# --- Шаги квеста ---
# riddle   — загадка, которую видит команда
# answer   — правильный ответ (ЗАГЛАВНЫМИ, бот примет любой регистр)
# fragment — осколок письма Черкаса, который выдаётся после верного ответа
# hint     — подсказка куда плыть дальше
STEPS = [
    {
        "riddle": """
📍 ТОЧКА 1 — ПЕРВАЯ ПРЕГРАДА

Стою поперёк реки и говорю течению: "Не пройдёшь."
Не замок, не стена — но не пускаю.
Черкас проклинал меня каждый раз, когда хотел пройти дальше.

Одним словом — кто я? ⚓
""",
        "answer": "ПЛОТИНА",
        "fragment": "Он не боится течения...",
        "hint": "🗺 Следующая цель — ищите лицо на стене над водой. Бледное, как сам Черкас после того выстрела. Вверх по Лопани!",
    },
    {
        "riddle": """
📍 ТОЧКА 2 — БЛЕДНОЕ ЛИЦО

Лицо смотрит со стены — без разрешения, без рамки, без галереи.
Художник пришёл ночью с баллончиком и сделал своё дело.
Полиция называет это хулиганством. Молодёжь — искусством.

Одним словом (итальянского происхождения) — как это называется? 🎨
""",
        "answer": "ГРАФФИТИ",
        "fragment": "...его лицо знакомо этим водам...",
        "hint": "🗺 Следующая цель — золотые купола видны с реки. Черкас шёл туда каяться. Помогло мало.",
    },
    {
        "riddle": """
📍 ТОЧКА 3 — ЗОЛОТЫЕ КУПОЛА

Черкас зашёл сюда перед смертью — исповедался.
Батюшка сказал: "Грехов многовато."
Черкас ответил: "Зато сокровище знатное."

Собор назван в честь дня, когда архангел Гавриил явился к Деве Марии и объявил великую весть.

Как называется этот праздник? ⛪
""",
        "answer": "БЛАГОВЕЩЕНИЕ",
        "fragment": "...он слышит, что шепчут реки...",
        "hint": "🗺 Следующая цель — торговая пристань. Черкас там закупался. И кое-что покрепче воды брал.",
    },
    {
        "riddle": """
📍 ТОЧКА 4 — ТОРГОВАЯ ПРИСТАНЬ

На этом рынке Черкас затаривался перед каждым походом.
Хлеб, мясо, специи — это всё дело.
Но любимее всего была одна жидкость.
Коричневая, крепкая, из тростника.
Без неё пират — не пират, а просто мужик в лодке.

Одним словом — что это? 🍺
""",
        "answer": "РОМ",
        "fragment": "...он находит путь там, где другие садятся на мель...",
        "hint": "🗺 Следующая цель — место, где людей бросают под купол и заставляют смеяться.",
    },
    {
        "riddle": """
📍 ТОЧКА 5 — ПОД КУПОЛОМ

Черкас заходил сюда однажды.
Акробаты, дрессированные звери, и один особый артист.
В красном носу. В огромных штанах.
Падает — встаёт. Снова падает — снова смеётся.

Черкас сказал: "Вот это настоящий моряк — никогда не сдаётся."

Кто этот артист? 🎪
""",
        "answer": "КЛОУН",
        "fragment": "...он не клоун и не фокусник...",
        "hint": "🗺 Последняя точка — туда, где Черкас умер. Где две реки перестают быть двумя. Вперёд, морские псы!",
    },
    {
        "riddle": """
📍 ТОЧКА 6 — МЕСТО ГИБЕЛИ ЧЕРКАСА

Вот оно. Место, где я умер.
Лопань и Харьков встречаются здесь и текут дальше — вместе.

Черкас ценил одного человека на корабле больше всех.
Не капитана, не боцмана.
Того, кто знает каждую мель и каждый изгиб реки.
Кто ведёт судно, не садясь на мель.
Кто привёл вас сюда сегодня.

Одним словом — кто это? 🌊
""",
        "answer": "ЛОЦМАН",
        "fragment": None,
        "hint": None,
    },
]

# --- Финал ---
FINALE_TEXT = """
⚓ Собираю письмо капитана Черкаса...

"Он не боится течения...
...его лицо знакомо этим водам...
...он слышит, что шепчут реки...
...он находит путь там, где другие садятся на мель...
...он не клоун и не фокусник..."

━━━━━━━━━━━━━━━━━━━━━━━

ЭТО ЛОЦМАН. 🏴‍☠️

А ваш лоцман сегодня — ДЕНЧИК.

Он молчал весь день.
Вёл вас.
Улыбался.
И знал, где сокровище — с самого начала.

Скромная морская сволочь. ☠️

━━━━━━━━━━━━━━━━━━━━━━━

ДЕНЧИК. ГДЕ ТАВЕРНА. ГДЕ ЕГЕРЬМЕЙСТЕР.

ОТВЕЧАЙ.

С уважением, ромом и восхищением к скромности —
Капитан Черкас 🏴‍☠️

P.S. С днём рождения, лоцман. Первый глоток — твой. 🥃
"""

# ================================================================
# КОД БОТА — ЗДЕСЬ ЛУЧШЕ НИЧЕГО НЕ МЕНЯТЬ
# ================================================================

# Состояние квеста: 0 = не начат, 1–6 = шаги, 7 = завершён
quest_step = 0


async def send_current_riddle(update: Update):
    """Отправить загадку текущего шага."""
    await update.message.reply_text(STEPS[quest_step - 1]["riddle"])


async def advance(update: Update):
    """Засчитать правильный ответ и перейти к следующему шагу."""
    global quest_step

    current = STEPS[quest_step - 1]

    # Показываем осколок письма
    if current["fragment"]:
        await update.message.reply_text(
            f'✉️ Осколок письма Черкаса:\n\n_{current["fragment"]}_',
            parse_mode="Markdown",
        )

    quest_step += 1

    if quest_step > len(STEPS):
        # Финал
        await update.message.reply_text(FINALE_TEXT)
    else:
        # Подсказка + следующая загадка
        if current["hint"]:
            await update.message.reply_text(current["hint"])
        await send_current_riddle(update)


async def bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправить вступление когда бот добавлен в группу."""
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await update.message.reply_text(INTRO_TEXT)
            break


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать квест — отправить подсказку к точке 1 и загадку."""
    global quest_step
    quest_step = 1
    await update.message.reply_text(START_HINT)
    await send_current_riddle(update)


async def cmd_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/skip черкас — пропустить текущий шаг (для администратора)."""
    global quest_step
    args = context.args
    if not args or args[0].lower() != ADMIN_PASSWORD:
        return  # Молча игнорируем — не показываем, что команда существует
    if quest_step == 0:
        await update.message.reply_text("Квест ещё не начат. Используй /start")
        return
    if quest_step > len(STEPS):
        await update.message.reply_text("Квест уже завершён.")
        return
    await update.message.reply_text("⚡ Шаг пропущен (команда администратора).")
    await advance(update)


async def cmd_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/restart черкас — перезапустить квест с начала (для администратора)."""
    global quest_step
    args = context.args
    if not args or args[0].lower() != ADMIN_PASSWORD:
        return
    quest_step = 0
    await update.message.reply_text("🔄 Квест перезапущен. Используй /start чтобы начать снова.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверять ответы участников."""
    if quest_step == 0 or quest_step > len(STEPS):
        return

    text = update.message.text.strip().upper()
    expected = STEPS[quest_step - 1]["answer"].upper()

    if text == expected:
        await advance(update)


def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("Переменная BOT_TOKEN не установлена!")

    app = Application.builder().token(token).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bot_added))
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("skip", cmd_skip))
    app.add_handler(CommandHandler("restart", cmd_restart))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен. Черкас одобряет. ☠️")
    app.run_polling()


if __name__ == "__main__":
    main()
