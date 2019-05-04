from cityorientation import app, db_teams, db_tasks, db_quests, db_templates, db_stat
from flask import render_template, redirect, url_for, request, send_from_directory
from random import shuffle
from werkzeug.utils import secure_filename
import datetime
import time
import logging
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
    quests = [*db_quests.find({})]
    for quest in quests:
        quest['complete'] = False
        template = db_templates.find_one({'template_id': quest['template_id']})
        quest['amount_of_cp'] = 0
        quest['template_name'] = 'не указан'
        start_time = datetime.datetime.fromtimestamp(max(1546290000, quest['start_time']))
        quest['date'] = start_time.strftime('%d-%m-%Y, %H:%M')
        duration = int(quest['duration'])
        quest['duration'] = ('0' + str(duration // 3600))[-2:] + ':' + ('0' + str(duration % 60))[-2:]
        if template is not None:
            quest['amount_of_cp'] = len(template['task_list'])
            quest['template_name'] = template['name']
    return render_template('listOfQuests.html', quests=quests, title="Квесты")


@app.route('/saveQuest', methods=['POST'])
def save_quest():
    form = request.form
    if 'quest_id' not in form:
        return redirect(url_for('list_of_quests'))
    if form['save'] == 'remove':
        db_quests.remove({'quest_id': form['quest_id']})
        return redirect(url_for('list_of_quests'))
    quest = {
        'quest_id': '',
        'template_id': '',
        'name': '',
        'place': '',
        'start_time': 1546290000, # 1 января 2019 года
        'duration': 3600
    }
    quest_id = form['quest_id']
    quest['quest_id'] = quest_id
    if 'template_id' in form:
        quest['template_id'] = form['template_id']
    if 'name' in form:
        quest['name'] = form['name']
    if 'place' in form:
        quest['place'] = form['place']
    if 'date' in form and 'time' in form:
        seconds = (datetime.date(*map(int, form['date'].split('-'))) - datetime.date(1970, 1, 1)).days
        seconds *= 24 * 60 * 60
        times = form['time'].split(':')
        seconds += int(times[0]) * 60 * 60 + int(times[1]) * 60
        seconds += time.timezone
        quest['start_time'] = max(seconds, 1546290000)
    if 'duration' in form:
        times = form['duration'].split(':')
        quest['duration'] = int(times[0]) * 60 * 60 + int(times[1]) * 60
    db_quests.update({'quest_id': quest_id}, {'$set': quest})

    return redirect(url_for('list_of_quests'))


@app.route('/addQuest', methods=['POST'])
def add_quest():
    num_quests = int(db_stat.find_one({'stat': 'stat'})['num_quests'])
    db_quests.insert({
        'quest_id': f'quest_id_{num_quests}',
        'template_id': '',
        'name': '',
        'place': '',
        'start_time': 1546290000, # 1 января 2019 года
        'duration': 3600
    })
    db_stat.update({'stat': 'stat'}, {'$set': {'num_quests': num_quests + 1}})
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
        task['answers'] = [elem.strip().lower() for elem in form['answers'].split(',')]
    if 'tip_1' in form:
        task['tips'][0] = form['tip_1']
    if 'tip_2' in form:
        task['tips'][1] = form['tip_2']

    db_tasks.update({'task_id': task_id}, {'$set': task})

    return redirect(url_for('list_of_tasks'))


@app.route('/listOfTeams', methods=['GET'])
def list_of_teams():
    teams = [*db_teams.find({})]
    for team in teams:
        team['quest_name'] = '-'
        if 'quest_id' in team:
            quest = db_quests.find_one({'quest_id': team['quest_id']})
            if quest is not None:
                team['quest_name'] = quest['name']
    return render_template('listOfTeams.html', teams=teams, title="Команды")


@app.route('/addTeam', methods=['POST'])
def add_team():
    num_team = int(db_stat.find_one({'stat': 'stat'})['num_team'])
    password = [e for e in 'abcdefghtyuipoi1234567890']
    shuffle(password)
    password = ''.join(password[:6])
    team = {'login': f'team{num_team}',
            'password': password,
            'team_name': f'Team {num_team}'}
    db_stat.update({'stat': 'stat'}, {'$set': {'num_team': str(num_team + 1)}})
    db_teams.insert(team)
    return redirect(url_for('list_of_teams'))


@app.route('/removeTeam/<login>', methods=['POST'])
def remove_team(login: str):
    db_teams.remove({'login': login})
    return redirect(url_for('list_of_teams'))


@app.route('/listOfTemplates', methods=['GET'])
def list_of_templates():
    templates = [*db_templates.find({})]
    return render_template('listOfTemplates.html', templates=templates, title="Шаблоны")


@app.route('/saveTemplate', methods=['POST'])
def save_template():
    form = request.form
    template = db_templates.find_one({'template_id': form['template_id']})
    if form['save'] == 'remove':
        db_templates.remove({'template_id': form['template_id']})
    elif form['save'] == 'addTask':
        template['name'] = form['name']
        template['task_list'].append(form['task_id'])
        db_templates.update({'template_id': form['template_id']}, {'$set': template})
        return redirect(f'{url_for("template_editor")}?template_id={template["template_id"]}')
    elif form['save'] == 'removeTask':
        template['name'] = form['name']
        template['task_list'].remove(form['task_id'])
        db_templates.update({'template_id': form['template_id']}, {'$set': template})
        return redirect(f'{url_for("template_editor")}?template_id={template["template_id"]}')
    else:
        db_templates.update({'template_id': form['template_id']}, {'$set': {'name': form['name']}})
    return redirect(url_for('list_of_templates'))


@app.route('/addTemplate', methods=['POST'])
def add_template():
    num_quests = int(db_stat.find_one({'stat': 'stat'})['num_templates'])
    db_templates.insert({
        'template_id': f'template_id_{num_quests}',
        'name': '',
        'task_list': []})
    db_stat.update({'stat': 'stat'}, {'$set': {'num_templates': num_quests + 1}})
    return redirect(url_for('list_of_templates'))


@app.route('/statistic/<quest_id>', methods=['GET'])
def statistic(quest_id):
    quest = db_quests.find_one({'quest_id': quest_id})
    teams = []
    template = db_templates.find_one({'template_id': db_quests.find_one({'quest_id': quest_id})['template_id']})
    amount_of_cp = len(template['task_list'])
    quest['amount_of_cp'] = amount_of_cp
    start_time = datetime.datetime.fromtimestamp(max(1546290000, quest['start_time']))
    quest['date'] = start_time.strftime('%d-%m-%Y, %H:%M')
    duration = int(quest['duration'])
    quest['duration'] = ('0' + str(duration // 3600))[-2:] + ':' + ('0' + str(duration % 60))[-2:]
    if 'progress' in quest:
        for login in quest['progress']:
            if db_teams.find_one({'login': login}) is None:
                db_quests.update({'quest_id': quest_id}, {'$unset': {f'progress.{login}': ""}})
                continue
            teams.append(dict())
            teams[-1]['name'] = db_teams.find_one({'login': login})['team_name']
            teams[-1]['times_complete'] = quest['progress'][login]['times_complete']
            for i in range(len(teams[-1]['times_complete'])):
                tm = int(teams[-1]['times_complete'][i])
                if tm == -1:
                    teams[-1]['times_complete'][i] = '-'
                else:
                    teams[-1]['times_complete'][i] = ('00' + str(tm//60//60))[-2:] + ':' + ('00' + str((tm//60) % 60))[-2:] + ':' + ('00' + str(tm % 60))[-2:]
            teams[-1]['tips'] = quest['progress'][login]['tips']
    return render_template('statistic.html', quest=quest, teams=teams, title="Статистика квеста")


@app.route('/templateEditor', methods=['GET'])
def template_editor():
    if 'template_id' in request.args:
        template = db_templates.find_one({'template_id': request.args['template_id']})
    all_tasks = [*db_tasks.find({})]
    selected_tasks = []
    remaining_tasks = []
    task_list = set(template['task_list'])
    for task in all_tasks:
        task = {
            'task_id': task['task_id'],
            'name': task['name'],
            'content': task['content']
        }
        if len(task['name']) >= 11:
            task['name'] = task['name'][:10] + '..'
        if len(task['content']) >= 13:
            task['content'] = task['content'][:12] + '..'
        if task['task_id'] in task_list:
            selected_tasks.append(task)
        else:
            remaining_tasks.append(task)

    return render_template('templateEditor.html', template=template, selected_tasks=selected_tasks,
                           remaining_tasks=remaining_tasks, title="Редактор шаблона")


@app.route('/questEditor', methods=['GET'])
def quest_editor():
    if 'quest_id' in request.args:
        quest = db_quests.find_one({'quest_id': request.args['quest_id']})
        start_time = datetime.datetime.fromtimestamp(max(1546290000, quest['start_time']))
        quest['time'] = start_time.strftime('%H:%M')
        quest['date'] = start_time.strftime('%Y-%m-%d')
        duration = quest['duration']
        quest['duration'] = ('0' + str(duration // 3600))[-2:] + ':' + ('0' + str(duration % 60))[-2:]
        templates = [*db_templates.find({})]
        if db_templates.find_one({'template_id': quest['template_id']}) is None:
            template_name = ''
        else:
            template_name = db_templates.find_one({'template_id': quest['template_id']})['name']
    return render_template('questEditor.html', quest=quest, templates=templates, template_name=template_name, title="Редактор квеста")
