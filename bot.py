import numpy as np
from keep_alive import keep_alive
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
keep_alive()
TOKEN = import os

TOKEN = os.getenv("TOKEN")

MAX_SIZE = 6

users = {}

# ================= MATEMATIK FUNKSIYALAR =================
def determinant(A):
    A = np.array(A, dtype=float)
    return np.linalg.det(A)

def inverse_matrix(A):
    A = np.array(A, dtype=float)
    if abs(np.linalg.det(A)) < 1e-10:
        return None
    return np.linalg.inv(A)
def solve_system_steps(A, b):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(A)

    aug = np.column_stack((A, b))
    text = "📘 Qadam-baqadam yechim (Gauss usuli)\n\n"

    # Forward elimination
    for i in range(n):
        # Pivot tekshirish
        if abs(aug[i][i]) < 1e-10:
            for k in range(i+1, n):
                if abs(aug[k][i]) > 1e-10:
                    aug[[i, k]] = aug[[k, i]]
                    text += f"{i+1}-qadam: {i+1} va {k+1} qator almashtirildi\n"
                    break

        # Pastdagi elementlarni nol qilish
        for j in range(i+1, n):
            factor = aug[j][i] / aug[i][i]
            aug[j] = aug[j] - factor * aug[i]
            text += f"{j+1}-qator = {j+1}-qator - ({factor:.3f}) * {i+1}-qator\n"

        text += "Matritsa holati:\n"
        for row in aug:
            text += " ".join(f"{v:.3f}" for v in row) + "\n"
        text += "\n"

    # Back substitution
    x = np.zeros(n)
    for i in range(n-1, -1, -1):
        x[i] = aug[i][n]
        for j in range(i+1, n):
            x[i] -= aug[i][j] * x[j]
        x[i] = x[i] / aug[i][i]

    text += "✅ Yakuniy yechim:\n"
    for i in range(n):
        text += f"x{i+1} = {x[i]:.6f}\n"

    return text


def solve_system(A, b):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    det = np.linalg.det(A)

    if abs(det) < 1e-10:
        rank_A = np.linalg.matrix_rank(A)
        rank_aug = np.linalg.matrix_rank(np.column_stack((A, b)))
        if rank_A == rank_aug:
            return "♾ Cheksiz ko‘p yechim mavjud."
        else:
            return "❌ Sistema yechimga ega emas."
    else:
        x = np.linalg.solve(A, b)
        text = "✅ Yechim:\n\n"
        for i, val in enumerate(x):
            text += f"x{i+1} = {val:.6f}\n"
        return text

# ================= MENYU =================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🔢 Matritsa bilan ishlash", callback_data="matrix")],
        [InlineKeyboardButton("👤 Mening ma'lumotlarim", callback_data="info")],
        [InlineKeyboardButton("🔄 Yangi boshlash", callback_data="restart")]
    ]
    return InlineKeyboardMarkup(keyboard)

def size_keyboard():
    keyboard = []
    row = []
    for i in range(2, MAX_SIZE + 1):
        row.append(InlineKeyboardButton(f"{i}×{i}", callback_data=f"size_{i}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("↩ Menyuga qaytish", callback_data="menu")])
    return InlineKeyboardMarkup(keyboard)

def matrix_keyboard(user):
    n = user["n"]
    A = user["A"]
    keyboard = []
    for i in range(n):
        row = []
        for j in range(n):
            val = A[i][j]
            text = str(val) if val is not None else f"a{i+1}{j+1}"
            row.append(InlineKeyboardButton(text, callback_data=f"set_{i}_{j}"))
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("🔍 Determinant", callback_data="det"),
        InlineKeyboardButton("🔄 Teskari", callback_data="inv"),
    ])
    keyboard.append([
        InlineKeyboardButton("Chiziqli algebraik  tenglamalar sistemasi(📐 Ax=b)", callback_data="solve")
    ])
    keyboard.append([
        InlineKeyboardButton("↩ Menyu", callback_data="menu")
    ])
    return InlineKeyboardMarkup(keyboard)

def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("↩ Orqaga", callback_data="back")],
        [InlineKeyboardButton("🏠 Menyu", callback_data="menu")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Matrix Solver Pro\n\nAsosiy menyu:",
        reply_markup=main_menu()
    )

# ================= TUGMALAR =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # ===== MENYU =====
    if data == "menu":
        await query.message.reply_text("Asosiy menyu:", reply_markup=main_menu())
        return

    if data == "matrix":
        await query.message.reply_text(
            "Matritsa o‘lchamini tanlang:",
            reply_markup=size_keyboard()
        )
        return

    if data == "restart":
        users.pop(user_id, None)
        await query.message.reply_text("Bot qayta boshlandi.", reply_markup=main_menu())
        return

    # ===== FOYDALANUVCHI MA'LUMOTI =====
    if data == "info":
        user = query.from_user
        text = (
            f"👤 Siz haqingizda:\n\n"
            f"ID: {user.id}\n"
            f"Ism: {user.first_name}\n"
            f"Username: @{user.username}\n"
        )

        if user_id in users:
            text += f"Tanlangan o‘lcham: {users[user_id].get('n', '-')}\n"

        await query.message.reply_text(text, reply_markup=main_menu())
        return

    # ===== O‘lcham tanlash =====
    if data.startswith("size"):
        n = int(data.split("_")[1])
        users[user_id] = {
            "n": n,
            "A": [[None]*n for _ in range(n)],
            "step": 0,
            "mode": "matrix"
        }
        await query.message.reply_text(
            f"{n}×{n} matritsa tanlandi.\na11 ni kiriting:",
            reply_markup=back_button()
        )
        return

    # ===== ORQAGA =====
    if data == "back":
        user = users.get(user_id)
        if user and user["step"] > 0:
            user["step"] -= 1
            i, j = divmod(user["step"], user["n"])
            user["A"][i][j] = None
            await query.message.reply_text(
                f"a{i+1}{j+1} ni qayta kiriting:",
                reply_markup=back_button()
            )
        return

    # ===== HISOBLASH =====
    if user_id not in users:
        return

    user = users[user_id]

    if data == "det":
        if None in sum(user["A"], []):
            await query.message.reply_text("Avval barcha elementlarni kiriting.")
            return
        det = determinant(user["A"])
        await query.message.reply_text(f"Determinant = {det:.6f}")

    elif data == "inv":
        if None in sum(user["A"], []):
            await query.message.reply_text("Avval barcha elementlarni kiriting.")
            return
        inv = inverse_matrix(user["A"])
        if inv is None:
            await query.message.reply_text("Bu matritsa teskari emas.")
        else:
            text = "Teskari matritsa:\n\n"
            for row in inv:
                text += " ".join(f"{v:.4f}" for v in row) + "\n"
            await query.message.reply_text(text)

    elif data == "solve":
        user["b"] = []
        user["mode"] = "b"
        user["step"] = 0
        await query.message.reply_text("1-ozod hadni kiriting:")

# ================= MATN =================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in users:
        return
    user = users[user_id]

    # Matritsa elementlari
    if user.get("mode") == "matrix":
        try:
            val = float(text)
            i, j = divmod(user["step"], user["n"])
            user["A"][i][j] = val
            user["step"] += 1

            if user["step"] < user["n"] * user["n"]:
                i2, j2 = divmod(user["step"], user["n"])
                await update.message.reply_text(
                    f"a{i2+1}{j2+1} ni kiriting:",
                    reply_markup=back_button()
                )
            else:
                await update.message.reply_text(
                    "Matritsa tayyor ✅",
                    reply_markup=matrix_keyboard(user)
                )
                user["mode"] = "done"
        except:
            await update.message.reply_text("Son kiriting.")
        return

    # Ozod hadlar
    if user.get("mode") == "b":
        try:
            user["b"].append(float(text))
            user["step"] += 1
            if user["step"] < user["n"]:
                await update.message.reply_text(f"{user['step']+1}-ozod had:")
            else:
                result = solve_system(user["A"], user["b"])
                await update.message.reply_text(result)

                # Qadam-baqadam yechim
                steps = solve_system_steps(user["A"], user["b"])

                for i in range(0, len(steps), 4000):
                    await update.message.reply_text(steps[i:i + 4000])

                users.pop(user_id, None)

        except:
            await update.message.reply_text("Son kiriting.")

# ================= ISHGA TUSHURISH =================
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

print("Bot ishga tushdi...")
app.run_polling()
