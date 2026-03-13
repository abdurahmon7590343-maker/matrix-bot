from flask import Flask
from threading import Thread

# Flask ilovasini yaratamiz
app = Flask('')

@app.route('/')
def home():
    # Bu matn brauzerda ko'rinadi (bot ishlayotganini bildiradi)
    return "Bot muvaffaqiyatli ishga tushirildi va uxlash rejimidan himoyalangan!"

def run():
    # Render 8080 yoki o'zi bergan portni ishlatadi
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    # Flask serverni alohida oqimda (thread) ishga tushiramiz
    # Shunda u botning asosiy ishiga xalaqit bermaydi
    t = Thread(target=run)
    t.start()