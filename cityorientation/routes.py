from cityorientation import app, db_teams, db_tasks, db_stat
from flask import render_template, redirect, url_for, request, send_from_directory
from random import shuffle
from werkzeug.utils import secure_filename
import os


@app.route('/')
def home():
    return redirect(url_for('list_of_quests'))


@app.route('/quest_images/<image>')
def get_image(image):
    uploads = os.path.join(app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=image)


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
    tasks = [*db_tasks.find({})]
    for task in tasks:
        task['answers'] = ','.join(task['answers'])
        task['tip_1'] = task['tips'][0]
        task['tip_2'] = task['tips'][1]

    return render_template('listOfTasks.html', tasks=tasks, title="Задания")


@app.route('/removeTask/<task_id>', methods=['GET'])
def remove_task(task_id):
    db_tasks.remove({'task_id': task_id})
    return redirect(url_for('list_of_tasks'))


@app.route('/addTask', methods=['POST'])
def add_task():
    num_tasks = int(db_stat.find_one({'stat': 'stat'})['num_tasks'])
    db_stat.update({'stat': 'stat'}, {'$set': {'num_tasks': str(num_tasks + 1)}})
    db_tasks.insert({
        'task_id': f'task_id_{num_tasks}',
        'name': '',
        'content': '',
        'img': '',
        'answers': [],
        'tips': ['', '']
    })
    return redirect(url_for('list_of_tasks'))


@app.route('/saveTask', methods=['POST'])
def save_task():
    form = request.form
    task = {
        'task_id': '',
        'name': '',
        'content': '',
        'img': '',
        'answers': [],
        'tips': ['', '']
    }
    if 'task_id' not in form:
        return redirect(url_for('list_of_tasks'))
    task_id = form['task_id']
    task['task_id'] = task_id
    if 'name' in form:
        task['name'] = form['name']
    if 'content' in form:
        task['content'] = form['content']
    if 'img' in form and form['img'] != '':
        task['img'] = form['img']
    elif 'img' not in form and 'last_img' in form: # Если была нажата кнопка удалить
        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], form['last_img'])):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], form['last_img']))
    if len(request.files) != 0:
        file = request.files.to_dict()['file']
        sfname = secure_filename(file.filename)
        ftype = sfname.split('.')[-1]
        if ftype in ['png', 'jpg']:
            img = f'{task_id}.{ftype}'
            task['img'] = img
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], img))
    if 'answers' in form:
        task['answers'] = [elem.strip() for elem in form['answers'].split(',')]
    if 'tip_1' in form:
        task['tips'][0] = form['tip_1']
    if 'tip_2' in form:
        task['tips'][1] = form['tip_2']
    print(task)

    db_tasks.update({'task_id': task_id}, {'$set': task})

    return redirect(url_for('list_of_tasks'))


@app.route('/listOfTeams', methods=['GET'])
def list_of_teams():
    teams = db_teams.find({}, {'_id': False})
    return render_template('listOfTeams.html', teams=teams, title="Команды")


@app.route('/addTeam', methods=['POST'])
def add_team():
    num_team = int(db_stat.find_one({'stat': 'stat'})['num_team'])
    password = [e for e in 'abcdefghtyuipoi1234567890']
    shuffle(password)
    password = ''.join(password[:6])
    team = {'login': f'team{num_team}',
            'password': password,
            'name': f'Team {num_team}'}
    db_stat.update({'stat': 'stat'}, {'$set': {'num_team': str(num_team + 1)}})
    db_teams.insert(team)
    return redirect(url_for('list_of_teams'))


@app.route('/removeTeam/<login>', methods=['POST'])
def remove_team(login: str):
    db_teams.remove({'login': login})
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
        {'name': 'Квест3', 'question': 'gertgwerg?', 'answer': 'wbfbw'}]
    return render_template('questEditor.html', editor=editor, etasks=etasks, title="Редактор квеста")
