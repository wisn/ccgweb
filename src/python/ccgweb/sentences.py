import ccgweb
import ccgweb.assignments
import ccgweb.users
import ccgweb.util
import falcon
import hashlib
import json
import os
import subprocess


class Sentence:

    def on_get(self, req, res, lang, sentence):
        assert lang in ['eng', 'deu', 'ita', 'nld']
        user = ccgweb.users.current_user(req)
        body = {}
        assignment = ccgweb.assignments.get_assignment(user if user else 'auto')
        for i, s in enumerate(assignment):
            if s['sentence'] == sentence:
                if i > 0:
                    body['prev'] = assignment[i - 1]['sentence']
                if i + 1 < len(assignment):
                    body['next'] = assignment[i + 1]['sentence']
                break
        auto_derxml, _ = get_contents(lang, sentence, 'auto', 'der.xml')
        body['auto_derxml'] = auto_derxml
        if user:
            user_derxml, marked_correct = get_contents(lang, sentence, user, 'der.xml')
            body['user_derxml'] = user_derxml
            body['marked_correct'] = marked_correct
        res.content_type = 'application/json'
        res.body = json.dumps(body)

    def on_post(self, req, res, lang, sentence):
        assert lang in ['eng', 'deu', 'ita', 'nld']
        if 'api_action' not in req.params:
            res.status = falcon.HTTP_400
            return
        if req.params['api_action'] == 'add_super_bow':
            user = ccgweb.users.current_user(req)
            if not user:
                res.status = falcon.HTTP_401
                return
            sentence_hash = sentence2hash(sentence)
            try:
                offset_from = int(req.params['offset_from'])
                offset_to = int(req.params['offset_to'])
                tag = req.params['tag']
            except (KeyError, ValueError):
                res.status = falcon.HTTP_400
                return
            ccgweb.db.execute('''INSERT INTO bows_super
                (user_id, time, lang, sentence_id, offset_from, offset_to, tag)
                VALUES (%s, NOW(), %s, %s, %s, %s, %s)''', user, lang,
                sentence_hash, offset_from, offset_to, tag)
        elif req.params['api_action'] == 'add_span_bow':
            user = ccgweb.users.current_user(req)
            if not user:
                res.status = falcon.HTTP_401
                return
            sentence_hash = sentence2hash(sentence)
            try:
                offset_from = int(req.params['offset_from'])
                offset_to = int(req.params['offset_to'])
            except (KeyError, ValueError):
                res.status = falcon.HTTP_400
                return
            ccgweb.db.execute('''INSERT INTO bows_span
                (user_id, time, lang, sentence_id, offset_from, offset_to)
                VALUES (%s, NOW(), %s, %s, %s,%s)''', user, lang, sentence_hash,
                offset_from, offset_to)
        elif req.params['api_action'] == 'mark_correct':
            user = ccgweb.users.current_user(req)
            if not user:
                res.status = falcon.HTTP_401
                return
            sentence_hash = sentence2hash(sentence)
            try:
                correct = req.params['correct'] == 'true'
            except KeyError:
                res.status = falcon.HTTP_400
                return
            if correct:
                with open(get_path(lang, sentence_hash, user, 'der.xml'), 'rb') as f:
                    derxml = f.read()
                ccgweb.db.execute('''INSERT INTO correct
                    (lang, sentence_id, user_id, time, derxml)
                    VALUES (%s, %s, %s, NOW(), %s)
                    ON DUPLICATE KEY UPDATE
                    time = NOW(), derxml = %s''', lang, sentence_hash,
                    user, derxml, derxml)
            else:
                ccgweb.db.execute('''DELETE FROM correct
                    WHERE lang = %s
                    AND sentence_id = %s
                    AND user_id = %s''', lang, sentence_hash, user)
        else:
            res.status = falcon.HTTP_400
            return


def sentence2hash(sentence):
    if not sentence.endswith('\n'):
        sentence += '\n'
    return hashlib.sha1(sentence.encode('UTF-8')).hexdigest()
    

def get_raw_path(lang, sentence_hash):
    raw_dir = os.path.join('raw', lang, sentence_hash[:2])
    return os.path.join(raw_dir, '.'.join((sentence_hash, 'raw')))


def get_path(lang, sentence_hash, user, extension):
    out_dir = os.path.join('out', lang, sentence_hash[:2], sentence_hash)
    return os.path.join(out_dir, '.'.join((user, extension)))


def get_contents(lang, sentence, user, extension):
    """Get the data for a specific annotation layer for some user.

    Returns a tuple (contents, marked_correct) where contents is the data as
    a string and marked_correct is boolean.
    """
    sentence_hash = sentence2hash(sentence)
    rows = ccgweb.db.get('''SELECT derxml
        FROM correct
        WHERE lang = %s
        AND sentence_id = %s
        AND user_id = %s''', lang, sentence_hash, user)
    if rows:
        return (rows[0][0], True)
    else:
        raw_path = get_raw_path(lang, sentence_hash)
        if not os.path.isfile(raw_path):
            ccgweb.util.makedirs(os.path.split(raw_path)[0])
            with open(raw_path, 'w', encoding='UTF-8') as f:
                f.write(sentence)
        der_path = get_path(lang, sentence_hash, user, 'der.xml')
        subprocess.check_call(('./ext/produce/produce', der_path))
        with open(der_path, 'r') as f:
            return (f.read(), False)