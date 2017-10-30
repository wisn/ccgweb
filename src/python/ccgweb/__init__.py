import falcon
import hashlib
import json
import MySQLdb
import os
import ccgweb.users
import ccgweb.util
import subprocess


class DB:

    def __init__(self, conn):
        self.conn = conn

    def get(self, sql, *args):
        with self.conn as cursor:
            cursor.execute(sql, args)
            return cursor.fetchall()

    def execute(self, sql, *args):
        with self.conn as cursor:
            cursor.execute(sql, args)


class Sentence:

    def on_get(self, req, res, sentence):
        sentence_hash = hashlib.sha1(sentence.encode('UTF-8')).hexdigest()
        hash_group = sentence_hash[:2]
        raw_dir = os.path.join('raw', hash_group)
        raw_file = os.path.join(raw_dir, sentence_hash + '.raw')
        out_dir = os.path.join('out', hash_group, sentence_hash)
        der_file = os.path.join(out_dir, 'auto.der.xml')
        if not os.path.isfile(raw_file):
            ccgweb.util.makedirs(raw_dir)
            with open(raw_file, 'w', encoding='UTF-8') as f:
                f.write(sentence)
        subprocess.check_call(('./ext/produce/produce', der_file))
        res.content_type = 'application/xml'
        with open(der_file, 'rb') as f:
            res.data = f.read()

    def on_post(self, req, res, sentence):
        if 'api_action' not in req.params:
            res.status = falcon.HTTP_400
            return
        if req.params['api_action'] == 'add_super_bow':
            user = ccgweb.users.current_user(req)
            if not user:
                res.status = falcon.HTTP_401
                return
            sentence_hash = hashlib.sha1(sentence.encode('UTF-8')).hexdigest()
            if 'offset_from' not in req.params \
                    or 'offset_to' not in req.params:
                res.status = falcon.HTTP_400
                return
            try:
                offset_from = int(req.params['offset_from'])
                offset_to = int(req.params['offset_to'])
            except ValueError:
                res.status = falcon.HTTP_400
                return
            db.execute('''INSERT INTO bows_super
                (user_id, time, sentence_id, offset_from, offset_to, tag)
                VALUES (%s, NOW(), %s, %s, %s, %s)''', user, sentence_hash,
                offset_from, offset_to, req.params['tag'])
        else:
            res.status = falcon.HTTP_400
            return


class Login:

    def on_post(self, req, res):
        session_id = ccgweb.users.login(req.params['user_id'],
                                        req.params['password'])
        if session_id:
            # TODO move this info to Set-Cookie header?
            body = { 'session_id': session_id }
            res.body = json.dumps(body)
        else:
            res.status = falcon.HTTP_401


class Session:

    def on_get(self, req, res):
        session_id = req.cookies['session_id']
        body = ccgweb.users.get_session_info(session_id)
        res.body = json.dumps(body)


with open('config.json') as f:
    config = json.load(f)


db = DB(MySQLdb.connect(config['db_host'], config['db_user'],
                        config['db_pass'], config['db_name']))