from cityorientation import app
from flask import render_template, redirect, url_for, request, send_from_directory


@app.route('/')
def home():
    return redirect(url_for('list_of_quests'))


@app.route('/listOfQuests', methods=['GET'])
def list_of_quests():
    quests = [
        {'name': 'В поисках Немо', 'date': '12 Февраля в 17:00', 'place': 'Петроградка', 'amount_of_cp': 17, 'complete': True},
        {'name': 'В поисках Немо', 'date': '12 Февраля в 17:00', 'place': 'Петрограftfдка', 'amount_of_cp': 100, 'complete': False}
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
        {'name': 'Квест2', 'question': '789456123', 'picture': 'picture.jpg', 'answer': '2345', 'tip_1': 'На зqwef нет', 'tip_2': '1234, 1234'},
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
        {'name': 'Шаблон2', 'duration': '4 часа', 'place': 'Вязьма', 'amount_of_cp': 100}
    ]
    return render_template('listOfTemplates.html', templates=templates, title="Шаблоны")


@app.route('/statistic', methods=['GET'])
def statistic():
    statistic = [
        {'level': '1', 'hint': '2'},
        {'level': '2', 'hint': '2'},
        {'level': '3', 'hint': '2'},
        {'level': '4', 'hint': '2'},
        {'level': '5', 'hint': '2'},
        {'level': '6', 'hint': '2'},
            ]
    return render_template('statistic.html', statistic=statistic, title="Статистика квеста")


@app.route('/templatesEditor', methods=['GET'])
def templates_editor():
    editor = [
        {'name': 'Шаблон1', 'date': '12-02-2019', 'duration': '4 часа', 'place': 'Петроградка', 'amount_of_cp': 17}
            ]
    etasks = [
        {'name': 'Квест1', 'question': 'qwefqwefqwef', 'answer': 'qwefqd'},
        {'name': 'Квест2', 'question': 'wergwergwerg', 'answer': 'rgtbwtr'},
        {'name': 'Квест3', 'question': 'qwefqwefqwef', 'answer': 'qwefsd'}
    ]
    return render_template('templatesEditor.html', editor=editor, etasks=etasks, title="Редактор шаблона")


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
    return render_template('questEditor.html', editor=editor, etasks=etasks, title="")

