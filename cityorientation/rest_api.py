from cityorientation import app, db_teams, db_quests, db_templates, db_tasks
from flask import request
from flask_restful import Resource, Api
from datetime import datetime, time

api = Api(app)
# Актуальная версия api
version = 'v1.0'


# Проверяет, что переданы корректные данные
def check_input_data(req, *args):
    if not req:
        return 'empty request'
    for arg in args:
        if arg not in req:
            return f"missing key '{arg}'"
        elif type(req[arg]) != str:
            return f"invalid type '{arg}'"
    return 'ok'


# Возвращает ok и team_name, если такая пара login-password существует
class LoginTeam(Resource):
    def post(self):
        req = request.get_json()
        ans = check_input_data(req, 'login', 'password')
        if ans != 'ok':
            return {'message': ans}

        team = db_teams.find_one({'login': req['login'], 'password': req['password']})
        if team is None:
            return {'message': 'team does not exist'}
        return {'message': 'ok', 'team_name': team['team_name']}


# Изменяет название команды
class RenameTeam(Resource):
    def post(self):
        req = request.get_json()
        ans = check_input_data(req, 'login', 'team_name')
        if ans != 'ok':
            return {'message': ans}

        team = db_teams.find_one({'login': req['login']})
        if team is None:
            return {'message': 'team does not exist'}
        db_teams.update({'login': req['login']}, {'$set': {'team_name': req['team_name']}})
        return {'message': 'ok'}


# Возвращает список квестов
class ListOfQuests(Resource):
    def post(self):
        list_of_quests = [*db_quests.find({}, {'_id': False, 'progress': False})]
        for quest in list_of_quests:
            template = db_templates.find_one({'template_id': quest['template_id']})
            quest['amount_of_cp'] = str(len(template['task_list']))
            quest.pop('template_id')
        return {'message': 'ok', 'list_of_quests': list_of_quests}


# Принять участие в Квесте
class JoinToQuest(Resource):
    def post(self):
        req = request.get_json()
        ans = check_input_data(req, 'login', 'quest_id')
        if ans != 'ok':
            return {'message': ans}
        if db_quests.find_one({'quest_id': req['quest_id']}) is None:
            return {'message': 'quest does not exist'}
        if db_teams.find_one({'login': req['login']}) is None:
            return {'message': 'team does not exist'}
        if db_quests.find_one({'quest_id': req['quest_id'],
                               f'progress.{req["login"]}': {'$exists': True}}) is not None:
            return {'message': 'team has already joined'}

        template = db_templates.find_one({'template_id': db_quests.find_one({'quest_id': req['quest_id']})['template_id']})
        amount_of_cp = len(template['task_list'])
        db_quests.update({'quest_id': req['quest_id']}, {'$set': {
            f'progress.{req["login"]}': {
                'personal_order': [i for i in range(amount_of_cp)],
                'times': [-1] * amount_of_cp,
                'times_complete': [-1] * amount_of_cp,
                'tips': [0] * amount_of_cp,
                'step': 0
            }
        }})
        return {'message': 'ok'}


# Возвращает список заданий
class ListOfTasks(Resource):
    def post(self):
        req = request.get_json()
        ans = check_input_data(req, 'login', 'quest_id')
        if ans != 'ok':
            return {'message': ans}
        if db_teams.find_one({'login': req['login']}) is None:
            return {'message': 'team does not exist'}
        if db_quests.find_one({'quest_id': req['quest_id']}) is None:
            return {'message': 'quest does not exist'}
        if db_quests.find_one({'quest_id': req['quest_id'],
                               f'progress.{req["login"]}': {'$exists': True}}) is None:
            return {'message': 'team has not joined this quest'}
        template_id = db_quests.find_one({'quest_id': req['quest_id']})['template_id']
        personal_order = db_quests.find_one(
            {'quest_id': req['quest_id'],
             f'progress.{req["login"]}': {'$exists': True}})['progress'][req["login"]]['personal_order']
        task_list = db_templates.find_one({'template_id': template_id})['task_list']
        ans = {'message': 'ok', 'tasks': []}
        tasks = []
        for pos in personal_order:
            task_id = task_list[pos]
            tasks.append(db_tasks.find_one({'task_id': task_id}, {'_id': False}))
        ans['tasks'] = tasks
        return ans


# Сохраняет в бд информацию о правильном вводе ответа на задачу
class CompleteTask(Resource):
    def post(self):
        req = request.get_json()
        ans = check_input_data(req, 'login', 'quest_id', 'task_number')
        if ans != 'ok':
            return {'message': ans}
        if db_teams.find_one({'login': req['login']}) is None:
            return {'message': 'team does not exist'}
        if db_quests.find_one({'quest_id': req['quest_id']}) is None:
            return {'message': 'quest does not exist'}
        if db_quests.find_one({'quest_id': req['quest_id'],
                               f'progress.{req["login"]}': {'$exists': True}}) is None:
            return {'message': 'team has not joined this quest'}
        progress = db_quests.find_one(
            {'quest_id': req['quest_id'],
             f'progress.{req["login"]}': {'$exists': True}})['progress'][req["login"]]
        times = progress['times']
        times_complete = progress['times_complete']
        step = int(progress['step'])
        task_number = int(req['task_number'])
        if task_number < 0 or task_number >= len(times):
            return {'message': 'task_number out of range'}

        delta = datetime.now() - datetime.combine(datetime.now().date(), time(0, 0))
        if int(times[task_number]) != -1:
            return {'message': 'task already complete'}
        elif task_number == 0:
            # В этом случае время прохождения первого задания - разница между текущим временем и
            # временем запуска самого квеста
            time_start = db_quests.find_one({'quest_id': req['quest_id']})['time']
            times_complete[task_number] = delta.seconds
            times[task_number] = delta.seconds - int(time_start)
            # Обновление массивов времён прохождения и номера текущего задания(step).
            # Берётся максимум т.к. возможна ситуация, когда придёт ответ на старое задание, и прогресс вернётся к
            # следующему после него заданию.
            db_quests.update({'quest_id': req['quest_id'], f'progress.{req["login"]}': {'$exists': True}},
                             {'$set': {
                                 f'progress.{req["login"]}.times': times,
                                 f'progress.{req["login"]}.times_complete': times_complete,
                                 f'progress.{req["login"]}.step': max(step, task_number + 1)
                             }})
            return {'message': 'ok'}
        else:
            # А здесь время прохождения задания - разница между текущим временем и временем финиша предыдущего
            times_complete[task_number] = delta.seconds
            times[task_number] = delta.seconds - times_complete[task_number - 1]
            db_quests.update({'quest_id': req['quest_id'], f'progress.{req["login"]}': {'$exists': True}},
                             {'$set': {
                                 f'progress.{req["login"]}.times': times,
                                 f'progress.{req["login"]}.times_complete': times_complete,
                                 f'progress.{req["login"]}.step': max(step, task_number + 1)
                             }})
            return {'message': 'ok'}


# Сохраняет в базу данных информацию о том, что использована подсказка
class UseTip(Resource):
    def post(self):
        req = request.get_json()
        ans = check_input_data(req, 'login', 'quest_id', 'task_number', 'tip_number')
        if ans != 'ok':
            return {'message': ans}
        if db_teams.find_one({'login': req['login']}) is None:
            return {'message': 'team does not exist'}
        if db_quests.find_one({'quest_id': req['quest_id']}) is None:
            return {'message': 'quest does not exist'}
        if db_quests.find_one({'quest_id': req['quest_id'],
                               f'progress.{req["login"]}': {'$exists': True}}) is None:
            return {'message': 'team has not joined this quest'}
        progress = db_quests.find_one(
            {'quest_id': req['quest_id'],
             f'progress.{req["login"]}': {'$exists': True}})['progress'][req["login"]]
        tips = progress['tips']
        task_number = int(req['task_number'])
        tip_number = int(req['tip_number'])
        if task_number < 0 or task_number >= len(tips):
            return {'message': 'task_number out of range'}
        if tip_number <= 0 or tip_number >= 3:
            return {'message': 'tip_number out of range'}
        if tips[task_number] >= tip_number:
            return {'message': 'tip has already used'}
        if tips[task_number] + 1 < tip_number:
            return {'message': 'need to use previous tip'}

        tips[task_number] = tip_number
        db_quests.update({'quest_id': req['quest_id'], f'progress.{req["login"]}': {'$exists': True}},
                         {'$set': {
                             f'progress.{req["login"]}.tips': tips}})
        return {'message': 'ok'}


api.add_resource(LoginTeam, f'/api/{version}/loginTeam')
api.add_resource(RenameTeam, f'/api/{version}/renameTeam')
api.add_resource(ListOfQuests, f'/api/{version}/listOfQuests')
api.add_resource(JoinToQuest, f'/api/{version}/joinToQuest')
api.add_resource(ListOfTasks, f'/api/{version}/listOfTasks')
api.add_resource(CompleteTask, f'/api/{version}/completeTask')
api.add_resource(UseTip, f'/api/{version}/useTip')
