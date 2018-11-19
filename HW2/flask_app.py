from flask import Flask, render_template, request

from db import DB, DBNAME, PASSWORD, UserExistsError


app = Flask(__name__)
_db = DB(DBNAME, PASSWORD)


def select_parser(op, args):
    cols = dict()
    query = dict()

    for k, v in args.items():
        if 'col_' in k:
            cols[k.split('col_')[1]] = True if v == 'on' else False

        elif k != 'op' and v:
            query[k] = v #if v else None

    # locking primary key columns to be always present
    cols['Id'] = True

    return cols, query


def write_parser(op, args):
    table_prefix = op.split('_')[0]
    values = {'%s_%s' % (table_prefix, k): v for k, v in args.items() if k != 'op'}
    
    if table_prefix == 'usr':
        values['usr_active'] = 1
   
    return [values]


def delete_parser(op, args):
    return [{'_id': int(args.get('_id'))}]


def update_parser(op, args):
    return [{k: v for k, v in args.items() if k != 'op' and v}]
    
    
def handle_request(request):
    args_raw = request.form if request.form else request.args
    op = args_raw.get('op')

    if op == 'commit':
        return handle_commit()
        
    handler = OP_HANDLERS[op.split('_')[1]]
    args_parser = OP_ARGS_PARSERS[op.split('_')[1]]

    args_parsed = [op]
    request_parsed = args_parser(op, args_raw)
    args_parsed.extend(request_parsed)
    
    response = handler(*args_parsed)
    
    return response


def handle_select(op, cols, query):
    response, col_names = _db.select(op, cols, query)
    
    if response and response[0].get('Active') == 0:
        op = 'delusr_select'

    return {
        'template_name_or_list': 'select.html',
        'response': response,
        'col_names': col_names,
        'op': op
    }

def handle_write(op, values):
    try:
        _db.write(op, values)

        return {
        'template_name_or_list': 'index.html',
        'status_log': 'OK'
    }

    except UserExistsError:
        return {
        'template_name_or_list': 'index.html',
        'status_log': 'User with this nick already exists'
    }


def handle_delete(op, values):
    _db.delete(op, values)
    return dict()


def handle_update(op, values):
    try:
        _db.update(op, values)
        return dict()

    except UserExistsError:
        return {
        'template_name_or_list': 'index.html',
        'status_log': 'User with this nick already exists'
    }


def handle_commit():
    _db.commit()

    return {
        'template_name_or_list': 'index.html',
        'status_log': ''
    }


OP_ARGS_PARSERS = {
    'select': select_parser,
    'write': write_parser,
    'delete': delete_parser,
    'update': update_parser
}

OP_HANDLERS = {
    'select': handle_select,
    'write': handle_write,
    'delete': handle_delete,
    'update': handle_update  
}



@app.route('/', methods=['GET', 'PUT', 'POST'])
def index():
    if request.args or request.form:
        response = handle_request(request)

    else:
        response = {
            'template_name_or_list': 'index.html',
            'status_log': ''
        }
            
    return render_template(**response)
    

@app.route('/select', methods=['GET', 'POST'])
def select():
    if request.args or request.form:
        response = handle_request(request)
        return render_template(**response) if response else ('OK', 204)
        
    return ('OK', 204)


@app.route('/usr_update', methods=['POST'])
def usr_update():
    form = request.form

    if form.get('_id') is not None:
        return render_template(
            'usr_update.html',
            op = form.get('op'),
            _id = form.get('_id'),
            status_log = ''
        )

    else:
        response = handle_request(request)
        return render_template(**response) if response else ('OK', 204)

    return ('OK', 204)


if __name__ == '__main__':
    app.run(debug=True)
