from flask import Flask, render_template, request
from db import FLDB

app = Flask(__name__)
db = FLDB('fldb.db')


def handle_fetch_all(table, form):
    response = db.fetch_all(table)
    report_message = 'Records: %s' % len(response) if response else 'Empty'
    return {'template_name_or_list': 'search_manage.html',
            'report_message': report_message,
            'response': response,
            'active_menu_id': table
           }

def handle_search_manage(table, form):
    values = {k: v for k, v in list(form.items())[1:] if v}
    query = ', '.join(['%s=%s' % (k, v) for k, v in values.items()])
    response = db.read(table, values)
    report_message = 'Query: %s' % query if response else 'Nothing found for query: %s' % query
    return {'template_name_or_list': 'search_manage.html',
            'report_message': report_message,
            'response': response,
            'active_menu_id': table
           }


def handle_write(table, form):
    values = {k: v for k, v in list(form.items())[1:] if v}
    db.write(table, values)
    report_message = 'OK'
    return {'template_name_or_list': 'index.html',
            'report_message': report_message,
            'active_menu_id': table,
            'active_sub_menu_id': 'write'
           }


def handle_remove(table, form):
    db.remove(table, form['remove_id'])
    return {}
    
    
def handle_assign(table, form):
    values = {k: v for k, v in list(form.items())[1:]}
    
    if table == 'projects':
        db.assign_project(values['record_id'], values['assigned_id'])
    else:
        db.assign_project(values['assigned_id'], values['record_id'])
    
    return {}


def handle_cancel(table, form):
    values = {k: v for k, v in list(form.items())[1:]}
    
    if table == 'projects':
        db.cancel_project(values['record_id'], values['prev_assigned_id'])
    else:
        db.cancel_project(values['prev_assigned_id'], values['record_id'])
        
    return {}


def handle_commit(table, form):
    db.commit()
    return {}


def handle_request(request):
    args = request.args if request.method == 'GET' else request.form
    
    if args:
        header = list(args.keys())[0]
        table = header.split('_')[0]
        op = '_'.join(header.split('_')[1:])
        
        handler = HANDLERS[op]
        response = handler(table, args)
        return response
    
    return {}

HANDLERS = {'fetch_all': handle_fetch_all,
            'search_manage': handle_search_manage,
            'write': handle_write,
            'remove': handle_remove,
            'assign': handle_assign,
            'cancel': handle_cancel,
            'commit': handle_commit
           }


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.form or request.args:
        response = handle_request(request)

    else:
        response = {'template_name_or_list': 'index.html',
                    'report_message': '',
                    'active_menu_id': 'none',
                    'active_sub_menu_id': 'none'
                   }
    if response:
        return render_template(**response)
    
    return ('OK', 204)
    
    
@app.route('/search_manage', methods=['GET', 'POST'])
def search_manage():
    response = handle_request(request)
    
    if response:
        return render_template(**response)
    
    return ('OK', 204)

            
if __name__ == '__main__':
    app.run()