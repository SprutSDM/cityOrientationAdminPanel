from cityorientation import app, db_teams, db_quests, db_templates, db_tasks
from flask import request
from flask_restful import Resource,  Api

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
            return {'answer': ans}

        team = db_teams.find_one({'login': req['login'], 'password': req['password']})
        if team is None:
            return {'answer': 'team does not exist'}
        return {'answer': 'ok', 'team_name': team['team_name']}


# Изменяет название команды
class RenameTeam(Resource):
    def post(self):
        req = request.get_json()
        ans = check_input_data(req, 'login', 'team_name')
        if ans != 'ok':
            return {'answer': ans}

        team = db_teams.find_one({'login': req['login']})
        if team is None:
            return {'answer': 'team does not exist'}
        db_teams.update({'login': req['login']}, {'$set': {'team_name': req['team_name']}})
        return {'answer': 'ok'}


# Возвращает список квестов
class ListOfQuests(Resource):
    def post(self):
        list_of_quests = [*db_quests.find({}, {'_id': False, 'progress': False, 'template_id': False})]
        for quest in list_of_quests:
            template = db_templates.find_one({'template_id': quest['template_id']})
            quest['amount_of_cp'] = str(len(template['task_list']))
        return {'answer': 'ok', 'list_of_quests': list_of_quests}


# Принять участие в Квесте
class JoinToQuest(Resource):
    def post(self):
        req = request.get_json()
        ans = check_input_data(req, 'login', 'quest_id')
        if ans != 'ok':
            return {'answer': ans}
        if db_quests.find_one({'quest_id': req['quest_id']}) is None:
            return {'answer': 'quest does not exist'}
        if db_teams.find_one({'login': req['login']}) is None:
            return {'answer': 'team does not exist'}
        if db_quests.find_one({'quest_id': req['quest_id'],
                               f'progress.{req["login"]}': {'$exists': True}}) is not None:
            return {'answer': 'team has already joined'}

        template = db_templates.find_one({'template_id': db_quests.find_one({'quest_id': req['quest_id']})['template_id']})
        amount_of_cp = len(template['task_list'])
        db_quests.update({'quest_id': req['quest_id']}, {'$set': {
            f'progress.{req["login"]}': {
                'personal_order': [i for i in range(amount_of_cp)],
                'times': [-1] * amount_of_cp,
                'tips': [0] * amount_of_cp,
                'step': 0
            }
        }})
        return {'answer': 'ok'}


# Возвращает список заданий
class ListOfTasks(Resource):
    def post(self):
        req = request.get_json()
        ans = check_input_data(req, 'login', 'quest_id')
        if ans != 'ok':
            return {'answer': ans}
        if db_teams.find_one({'login': req['login']}) is None:
            return {'answer': 'team does not exist'}
        if db_quests.find_one({'quest_id': req['quest_id']}) is None:
            return {'answer': 'quest does not exist'}
        template_id = db_quests.find_one({'quest_id': req['quest_id']})['template_id']
        personal_order = db_quests.find_one(
            {'quest_id': req['quest_id'],
             f'progress.{req["login"]}': {'$exists': True}})['progress'][req["login"]]['personal_order']
        task_list = db_templates.find_one({'template_id': template_id})['task_list']
        ans = {'answer': 'ok', 'tasks': []}
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
        check_input_data(req, 'login', 'quest_id', 'task_number')


api.add_resource(LoginTeam, f'/api/{version}/loginTeam')
api.add_resource(RenameTeam, f'/api/{version}/renameTeam')
api.add_resource(ListOfQuests, f'/api/{version}/listOfQuests')
api.add_resource(JoinToQuest, f'/api/{version}/joinToQuest')
api.add_resource(ListOfTasks, f'/api/{version}/listOfTasks')
