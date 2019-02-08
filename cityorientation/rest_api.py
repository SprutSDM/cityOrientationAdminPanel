from cityorientation import app, db_teams, db_quests
from flask import request
from flask_restful import Resource,  Api

api = Api(app)


# Проверяет, что переданы корректные данные
def check_input_data(req, *args):
    for arg in args:
        if arg not in req:
            return f"missing key '{arg}'"
        elif type(req[arg]) != str:
            return f"invalid type '{arg}'"
    return 'ok'


# Возвращает ok и team_name, если такая пара login-password существует
class LoginTeam(Resource):
    def get(self):
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
    def get(self):
        list_of_quests = [*db_quests.find({}, {'_id': False})]
        print(list_of_quests)
        return {'answer': list_of_quests}


api.add_resource(LoginTeam, '/api/loginTeam')
api.add_resource(RenameTeam, '/api/renameTeam')
api.add_resource(ListOfQuests, '/api/listOfQuests')
