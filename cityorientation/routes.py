from cityorientation import app
from flask import render_template, redirect, url_for, request, send_from_directory


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/listOfQuests', methods=['GET'])
def list_of_quests():
    quests = [
        {'name': 'В поисках Немо', 'date': '12 Февраля в 17:00', 'place': 'Петроградка', 'amount_of_cp': 17}
    ]
    return render_template('listOfQuests.html', quests=quests)
