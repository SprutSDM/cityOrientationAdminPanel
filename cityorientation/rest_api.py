from cityorientation import app, db_teams, db_quests, db_templates, db_tasks
from flask import request
from flask_restful import Resource, Api
import datetime
import time

api = Api(app)
# Актуальная версия api
version = 'v1'


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
class SignUp(Resource):
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
    def get(self):
        list_of_quests = [*db_quests.find({}, {'_id': False, 'progress': False})]
        for quest in list_of_quests:
            template = db_templates.find_one({'template_id': quest['template_id']})
            quest['amount_of_cp'] = str(len(template['task_list']))

            quest.pop('template_id')
        return {'message': 'ok', 'count': len(list_of_quests), 'list_of_quests': list_of_quests}


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
            db_teams.update({'login': req['login']}, {'$set': {'quest_id': req['quest_id']}})
            return {'message': 'ok'}
        if db_teams.find_one({'login': req['login'], 'quest_id': {'$exists': False}}) is None:
            return {'message': 'team has joined to another quest'}

        template = db_templates.find_one({'template_id': db_quests.find_one({'quest_id': req['quest_id']})['template_id']})
        amount_of_cp = len(template['task_list'])
        db_quests.update({'quest_id': req['quest_id']}, {'$set': {
            f'progress.{req["login"]}': {
                'personal_order': [i for i in range(amount_of_cp)],
                'times': [-1] * amount_of_cp,
                'times_complete': [-1] * amount_of_cp,
                'tips': [[False, False] for i in range(amount_of_cp)],
                'step': 0
            }
        }})
        db_teams.update({'login': req['login']}, {'$set': {'quest_id': req['quest_id']}})
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
            return {'message': 'team has not joined to this quest'}
        progress = db_quests.find_one(
            {'quest_id': req['quest_id'],
             f'progress.{req["login"]}': {'$exists': True}})['progress'][req["login"]]
        times_complete = progress['times_complete']
        step = int(progress['step'])
        task_number = int(req['task_number'])
        if task_number < 0 or task_number >= len(times_complete):
            return {'message': 'task_number out of range'}

        if int(times_complete[task_number]) != -1:
            return {'message': 'task already complete'}

        quest = db_quests.find_one({'quest_id': req['quest_id']})
        times_complete[task_number] = int(time.time()) - int(quest['start_time'])
        db_quests.update({'quest_id': req['quest_id'], f'progress.{req["login"]}': {'$exists': True}},
                         {'$set': {
                             f'progress.{req["login"]}.times_complete': times_complete,
                             f'progress.{req["login"]}.step': max(step, task_number + 1)
                         }})
        return {'message': 'ok', 'time_complete': times_complete[task_number]}


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
        if tip_number < 0 or tip_number >= 2:
            return {'message': 'tip_number out of range'}

        tips[task_number][tip_number] = True
        db_quests.update({'quest_id': req['quest_id'], f'progress.{req["login"]}': {'$exists': True}},
                         {'$set': {
                             f'progress.{req["login"]}.tips': tips}})
        return {'message': 'ok'}


# Вовзаращет текущее состояние
class GetState(Resource):
    def post(self):
        req = request.get_json()
        ans = check_input_data(req, 'login')
        response = {
                'message': '',
                'quest_id': '',
                'team_name': '',
                'times_complete': [],
                'step': 0,
                'seconds': int(time.time() * 1000),
                'time_zone': time.timezone,
                'tips': []
        }
        if ans != 'ok':
            response['message'] = ans
            return response
        if db_teams.find_one({'login': req['login']}) is None:
            response['message'] = ans
            return response
        team = db_teams.find_one({'login': req['login']})

        response['message'] = 'ok'
        response['team_name'] = team['team_name']
        if 'quest_id' not in team:
            return response

        quest_id = team['quest_id']
        # Если команда вступила в какой то квест, а его уже не существует, то удаляем о нём упоминание
        if db_quests.find_one({'quest_id': quest_id,
                               f'progress.{req["login"]}': {'$exists': True}}) is None:
            db_teams.update({'login': req['login']}, {'$unset': {'quest_id': True}})
            return response

        # quest = db_quests.find_one(db_quests.find_one({'quest_id': quest_id}))
        # if int(quest['date']) < int(time.time() // 86400):
        #     db_teams.update({'login': req['login']}, {'$unset': {'quest_id': True}})
        #     return {'message': 'ok'}
        #
        # if int(quest['time']) + int(quest['duration']) < (datetime.datetime.now() - datetime.datetime.combine(
        #         datetime.datetime.now().date(), datetime.time(0, 0))).seconds:
        #     db_teams.update({'login': req['login']}, {'$unset': {'quest_id': True}})
        #     return {'message': 'ok'}
        progress = db_quests.find_one({'quest_id': team['quest_id']})['progress'][req['login']]
        response['quest_id'] = team['quest_id']
        response['times_complete'] = progress['times_complete']
        response['step'] = progress['step']
        response['tips'] = progress['tips']
        print(response)
        return response


class LeaveQuest(Resource):
    def post(self):
        req = request.get_json()
        ans = check_input_data(req, 'login')
        if ans != 'ok':
            return {'message': ans}
        if db_teams.find_one({'login': req['login']}) is None:
            return {'message': 'team does not exist'}
        db_teams.update({'login': req['login']}, {'$unset': {'quest_id': ''}})
        return {'message': 'ok'}


api.add_resource(SignUp, f'/api/{version}/signUp')
api.add_resource(RenameTeam, f'/api/{version}/renameTeam')
api.add_resource(ListOfQuests, f'/api/{version}/quests')
api.add_resource(JoinToQuest, f'/api/{version}/joinToQuest')
api.add_resource(ListOfTasks, f'/api/{version}/tasks')
api.add_resource(CompleteTask, f'/api/{version}/completeTask')
api.add_resource(UseTip, f'/api/{version}/useTip')
api.add_resource(GetState, f'/api/{version}/getState')
api.add_resource(LeaveQuest, f'/api/{version}/leaveQuest')
