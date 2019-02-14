from cityorientation import app
from flask import render_template, redirect, url_for, request, send_from_directory


@app.route('/')
def home():
    return redirect(url_for('list_of_quests'))


@app.route('/listOfQuests', methods=['GET'])
def list_of_quests():
    quests = [
        {'name': 'В поисках Немо', 'date': '12 Февраля в 17:00', 'place': 'Петроградка', 'amount_of_cp': 17, 'duration':'4 часа', 'complete': True},
        {'name': 'В поисках Немо', 'date': '12 Февраля в 17:00', 'place': 'Петрограftfдка', 'amount_of_cp': 100, 'duration':'4 часа', 'complete': False}
    ]
    return render_template('listOfQuests.html', quests=quests, title="Квесты")


@app.route('/addQuest', methods=['GET'])
def add_quest():
    return redirect(url_for('list_of_quests'))


@app.route('/removeQuest', methods=['GET'])
def remove_quest():
    return redirect(url_for('list_of_quests'))


@app.route('/listOfTasks', methods=['GET'])
def list_of_tasks():
    tasks = [
        {'name': 'Квест1', 'question': '123456', 'picture': 'picture.jpg', 'answer': '1234', 'tip_1': 'Нqefwт', 'tip_2': 'П3424123414234'},
        {'name': 'Квест2', 'question': '789456123', 'picture': '', 'answer': '2345', 'tip_1': 'На зqwef нет', 'tip_2': '1234, 1234'},
        {'name': 'Квест3', 'question': 'qewmfqwkljefnlqkwjebflqkjwenflkqwjneflkqjwenflkqjwefqwefqw', 'picture': 'picture.jpg', 'answer': '3465', 'tip_1': 'f4f32', 'tip_2': 'f234f'}
    ]
    return render_template('listOfTasks.html', tasks=tasks, title="Задания")


@app.route('/addTask', methods=['GET'])
def add_task():
    return render_template('addtask.html', title="Добавление нового задания")


@app.route('/listOfTeams', methods=['GET'])
def list_of_teams():
    teams = [
        {'name': 'Команда1', 'login': 'team1', 'password': '1234'},
        {'name': 'Команда2', 'login': 'team2', 'password': '1234'},
        {'name': 'Команда3', 'login': 'team3', 'password': '1234'}
    ]
    return render_template('listOfTeams.html', teams=teams, title="Команды")


@app.route('/addTeam', methods=['GET'])
def add_team():
    return redirect(url_for('list_of_teams'))


@app.route('/listOfTemplates', methods=['GET'])
def list_of_templates():
    templates = [
        {'name': 'Шаблон1', 'duration': '4 часа', 'place': 'Петроградка', 'amount_of_cp': 17},
        {'name': 'Шаблон2', 'duration': '4 часа', 'place': 'Вязьма', 'amount_of_cp': 100},
    ]
    return render_template('listOfTemplates.html', templates=templates, title="Шаблоны")


@app.route('/statistic', methods=['GET'])
def statistic():
    statistic = [{'name': 'команда1', 'time1': '0:20', 'hint1': '0/2', 'time2': '0:20', 'hint2': '0/2', 'time3': '0:20', 'hint3': '0/2', 'time4': '0:20', 'hint4': '0/2', 'time5': '0:20', 'hint5': '0/2', 'time6': '0:20', 'hint6': '0/2', 'time7': '0:20', 'hint7': '0/2', 'time8': '0:20', 'hint8': '0/2', 'time9': '0:20', 'hint9': '0/2', 'time10': '0:20', 'hint10': '0/2', 'time11': '0:20', 'hint11': '0/2', 'time12': '0:20', 'hint12': '0/2', 'time13': '0:20', 'hint13': '0/2', 'time14': '0:20', 'hint14': '0/2', 'time15': '0:20', 'hint15': '0/2', 'time16': '0:20', 'hint16': '0/2', 'time17': '0:20', 'hint17': '0/2', 'time18': '0:20', 'hint18': '0/2', 'time19': '0:20', 'hint19': '0/2'} for i in range(50)]
    kvest = [{'name': 'Квест1', 'date': '12-02-2019', 'duration': '4 часа', 'place': 'Петроградка'}]
    return render_template('statistic.html', statistic=statistic, kvest=kvest, title="Статистика квеста")


@app.route('/templatesEditor', methods=['GET'])
def templates_editor():
    editor = [
        {'name': 'Шаблон1', 'date': '12-02-2019', 'duration': '4 часа', 'place': 'Петроградка', 'amount_of_cp': 17}
            ]
    etasks = [
        {'name': 'Квест1', 'question': 'qwefqwefqwef', 'answer': 'qwefqd'},
        {'name': 'Квест2', 'question': 'wergwergwerg', 'answer': 'rgtbwtr'},
        {'name': 'Квест3', 'question': 'qwefqwefqwef', 'answer': 'qwefsd'},
        {'name': 'Квест3', 'question': 'qwefqwefqwef', 'answer': 'qwefsd'}
    ]
    return render_template('templatesEditor.html', editor=editor, etasks=etasks, title="Редактор шаблон")


@app.route('/questEditor', methods=['GET'])
def quest_editor():
    editor = [
        {'name': 'Шаблон1', 'date': '12-02-2019', 'duration': '4 часа', 'place': 'Петроградка', 'amount_of_cp': 17}
            ]
    etasks = [
        {'name': 'Квест1', 'question': '12341234', 'answer': 'wergwfv'},
        {'name': 'Квест2', 'question': 'qwefqwefз?', 'answer': 'wergwbw'},
        {'name': 'Квест3', 'question': 'gertgwerg?', 'answer': 'wbfbw'}
    ]
    return render_template('questEditor.html', editor=editor, etasks=etasks, title="Редактор квеста")
