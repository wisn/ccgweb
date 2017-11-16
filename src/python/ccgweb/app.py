import ccgweb.assignments
import ccgweb.sentences
import ccgweb.users
import falcon


application = falcon.API()

if hasattr(application.req_options, 'auto_parse_form_urlencoded'):
    application.req_options.auto_parse_form_urlencoded = True

application.add_route('/sentences/{lang}/{sentence}/{user_id}', ccgweb.sentences.Sentence())
application.add_route('/session', ccgweb.users.Session())
application.add_route('/assignment', ccgweb.assignments.Assignment())
