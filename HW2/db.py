import re
import psycopg2


DBNAME = 'chat.db'
PASSWORD = 'testpassword1010'


class UserExistsError(Exception):
    """raised when writting user with existing nick"""

class DB:

    def __init__(self, dbname, password):
        self.dbname = dbname

        self.conn = psycopg2.connect(dbname=dbname,
                                     password=password,
                                     user='postgres',
                                     host='localhost'
        )
        
        self.cursor = self.conn.cursor()
        
        self.INSERT_CMD_TEMPLATE = \
        """
        INSERT INTO __TABLE_PLACEHOLDER__ __COLS_PLACEHOLDER__
        VALUES __VALS_PLACEHOLDER__;
        """

        self.UPDATE_CMD_TEMPLATE = \
        """
        UPDATE __TABLE_PLACEHOLDER__
        SET __SET_PLACEHOLDER__
        WHERE usr_id = %s;
        """

        self.CMD_TEMPLATES = {
        'msg_select':
        """
        SELECT
        __COLS_PLACEHOLDER__

        FROM Messages as msg

        INNER JOIN Users as usr_send
        ON msg.msg_usr_id_from = usr_send.usr_id

        INNER JOIN  
            (SELECT * FROM Users
             UNION
             SELECT * FROM DelUsers
            ) as usr_rec
        ON msg.msg_usr_id_to = usr_rec.usr_id
        
        __WHERE_PLACEHOLDER__
        """,

        'usr_select':
        """
        SELECT
        __COLS_PLACEHOLDER__

        FROM Users

        __WHERE_PLACEHOLDER__
        """
        }
        
        self.OP_TO_TABLE_NAME_MAP = {
            'msg_select': 'Messages',
            'usr_select': 'Users',
            'msg_write': 'Messages',
            'usr_write': 'Users',
            'delusr_write': 'DelUsers'
        }

        self.SELECT_CMD_COLS_MAP = {
            'msg_select': 
                {
                    'Id': 'msg.msg_id as Id',
                    'Content': 'msg.msg_content as Content',
                    'Date': 'msg.msg_date as Date',
                    'SenderId': 'usr_send.usr_id as SenderId',
                    'SenderNick': 'usr_send.usr_nick as SenderNick', 
                    'SenderName': 'usr_send.usr_name as SenderName',
                    'RecipientId': 'usr_rec.usr_id as RecipientId',
                    'RecipientNick': 'usr_rec.usr_nick as RecipientNick',
                    'RecipientName': 'usr_rec.usr_name as RecipientName',
                    'RecipientActive': 'usr_rec.usr_active as RecipientActive'
                },

            'usr_select':
                {   
                    'Id': 'usr_id as Id',
                    'Nick': 'usr_nick as Nick',
                    'Name': 'usr_name as Name',
                    'Bio': 'usr_bio as Bio',
                    'Active': 'usr_active as Active'
                }
        }

        self.SELECT_CMD_WHERE_ATRS_MAP = {
            'msg_select':
                {
                    '_id': ('msg.msg_id', '=', False),
                    'from_id': ('msg.msg_usr_id_from', '=', False),
                    'to_id': ('msg.msg_usr_id_to', '=', False),
                    'from_nick': ('usr_send.usr_nick', None, True),
                    'to_nick': ('usr_rec.usr_nick', None, True),
                    'from_name': ('usr_send.usr_name', None, True),
                    'to_nick': ('usr_rec.usr_name', None, True),
                    'to_active': ('usr_rec.usr_active', '=', False),
                    'content': ('msg.msg_content', None, True),
                    'from_date': ('msg.msg_date', '>=', False),
                    'to_date': ('msg.msg_date', '<=', False),
                },

            'usr_select':
                {   
                    '_id': ('usr_id', '=', False),
                    'nick': ('usr_nick', None, True),
                    'name': ('usr_name', None, True),
                    'bio': ('usr_bio', None, True),
                    'active': ('usr_active', '=', False)
                }
        }

        self.FETCH_COLS_TO_HTML_COLS_MAP = {
            'msg_select': 
                {
                    'id': 'Id',
                    'content': 'Content',
                    'date': 'Date',
                    'senderid': 'SenderId', 
                    'sendernick': 'SenderNick', 
                    'sendername': 'SenderName',
                    'recipientid': 'RecipientId',
                    'recipientnick': 'RecipientNick',
                    'recipientname': 'RecipientName',
                    'recipientactive': 'RecipientActive'
                },

            'usr_select':
                {   
                    'id': 'Id',
                    'nick': 'Nick',
                    'name': 'Name',
                    'bio': 'Bio',
                    'active': 'Active'
                }
        }

    def create_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE Users (
                usr_id SERIAL PRIMARY KEY,
                usr_nick TEXT,
                usr_name TEXT,
                usr_bio TEXT,
                usr_active INTEGER
            );
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE DelUsers (
                usr_id INTEGER PRIMARY KEY,
                usr_nick TEXT,
                usr_name TEXT,
                usr_bio TEXT,
                usr_active INTEGER 
            );
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE Messages (
                msg_id SERIAL PRIMARY KEY,
                msg_usr_id_from INTEGER,
                msg_usr_id_to INTEGER,
                msg_content TEXT,
                msg_date TEXT
            );
            """
        )

    def __fill_dummy_users(self):
        self.cursor.execute(
            """
            INSERT INTO Users (usr_nick, usr_name, usr_bio, usr_active)
            VALUES ('CHAT', 'COMMON_CHAT', 'none', 1),
                   ('mikeg', 'Mike G.', 'Hey, I''m Mike', 1),
                   ('jamesh', 'James H.', 'What''s up, James here', 1),
                   ('spy', 'nameless', 'classified', 1);
            """
        )

    def __fill_dummy_messages(self):
        self.cursor.execute(
            """
            INSERT INTO Messages (msg_usr_id_from, msg_usr_id_to, msg_content, msg_date)
            VALUES (2, 3, 'Hey!', '20181031'),
                   (3, 2, 'whats up!', '20181101'),
                   (2, 1, 'hey y''all!', '20181101'),
                   (4, 2, 'i see ya', '20181103'),
                   (2, 4, 'who r u?', '20181104');
            """
        )

    def fill_dummies(self):
        self.__fill_dummy_users()
        self.__fill_dummy_messages()

    def commit(self):
        self.conn.commit()

    def fetch_dicts(self, op):
        data = self.cursor.fetchall()
        res = list()
        col_names_map = self.FETCH_COLS_TO_HTML_COLS_MAP[op] 

        for record in data:
            d = dict()
            
            for idx, col in enumerate(self.cursor.description):
                col_name = col_names_map[col.name]
                d[col_name] = record[idx]
            
            res.append(d)
        
        return res

    def __fill_cols_cmd_placeholder(self, op, cols):
        """cols: dict({col_name: True|False})"""

        return ',\n'.join([self.SELECT_CMD_COLS_MAP[op][col_name]
                           for col_name, col_include in cols.items() if col_include
                          ]
        )

    def __fill_where_cmd_placeholder(self, op, query):
        """
        return: exp: str: WHERE expression
                args: list: args to fill %s in `exp`        
        """

        exps = list()
        args = list()

        atr_map = self.SELECT_CMD_WHERE_ATRS_MAP[op]

        for atr, value in query.items():
            if value:
                _atr, operator, if_bool_like_exp = atr_map[atr]

                if if_bool_like_exp:
                    c_exp, c_args = self.__parse_bool_like_query(_atr, value)

                    c_exp = '(%s)' % c_exp if c_exp else c_exp
                    exps.append(c_exp)
                    args.extend(c_args)

                else:
                    c_exp = '%s %s %s' % (_atr, operator, '%s') 

                    exps.append(c_exp)
                    args.append(value)

        exp = 'WHERE\n%s' % '\nAND\n'.join(exps) if exps else str()
        args = tuple(args)

        return exp, args

    def __get_cmd_template(self, op, query):
        cmd = self.CMD_TEMPLATES[op]

        # SELECTING FROM DELUSERS
        if op == 'usr_select' and query.get('active') == '0':
            cmd = re.sub('Users', 'DelUsers', cmd)

        return cmd

    def __parse_select_expression(self, op, cols, query):
        cmd = self.__get_cmd_template(op, query)

        # FILLING COLS TO SELECT
        
        cols_exp = self.__fill_cols_cmd_placeholder(op, cols)
        cmd = re.sub('__COLS_PLACEHOLDER__', cols_exp, cmd)

        # FILLING WHERE EXPRESSION

        where_exp, where_args = self.__fill_where_cmd_placeholder(op, query)
        cmd = re.sub('__WHERE_PLACEHOLDER__', where_exp, cmd)

        cmd = cmd.strip()
        cmd = re.sub(' {2,}', '', cmd)
        cmd += ';'

        return cmd, where_args


    def __parse_bool_like_query(self, attribute, query):
        query = str(query)
        args, values = self.__parse_bool_like_args(attribute, query)
        ops = self.__parse_bool_like_ops(query)

        if not ops:
            return ' '.join(args), values

        if len(args) < 2:
            raise Exception('invalid query')

        assert len(args) - len(ops) == 1

        res = list()

        res.extend([args[0], ops[0], args[1]])
        i = 2
        j = 1

        while j < len(ops):
            res.extend([ops[j], args[i]])
            i += 1
            j += 1

        return ' '.join(res), values
        
    def __parse_bool_like_args(self, attribute, query):
        args_raw = re.split('[&|\|]', query)

        args = list()
        values = list()

        for arg_raw in args_raw:
            arg_raw = arg_raw.strip()

            if '%' in arg_raw or '_' in arg_raw:
                arg = '%s LIKE %s' % (attribute, '%s')
                values.append(re.sub('[\(\)]', '', arg_raw))

            else:
                arg = '%s = %s' % (attribute, '%s')
                values.append(re.sub('[\(\)]', '', arg_raw))

            if arg_raw.startswith('('):
                arg = '(' * arg_raw.count('(') + arg

            if arg_raw.endswith(')'):
                arg += ')' * arg_raw.count(')')

            args.append(arg)

        return args, values

    def __parse_bool_like_ops(self, query):
        ops = re.sub('[^&|]', ' ', query)
        ops = re.sub(' +', ' ', ops)
        ops = ops.strip()
        ops = ops.split()
        ops = list(map(lambda x: 'AND' if x == '&' else 'OR', ops))
        return ops

    def __select(self, op, cmd, args):
        self.cursor.execute(cmd, args)

        return self.fetch_dicts(op)

    def select(self, op, columns, query):
        """
        columns: columns to fetch with SELECT
                dict({col_name: True|False})
        query: GET query
               dict({atr: value})

        return: fetched values <dict>, col names <list>
        """

        if not query:
            return dict(), list()

        cmd, args = self.__parse_select_expression(op, columns, query)
        col_names = list(columns.keys())
        return self.__select(op, cmd, args), col_names
    
    def __parse_write_expression(self, op, values):
        table_name = self.OP_TO_TABLE_NAME_MAP[op]
        cmd = self.INSERT_CMD_TEMPLATE
        args = list()
        
        cmd = re.sub('__TABLE_PLACEHOLDER__', table_name, cmd)
        
        cols_filler = '(%s)' % ', '.join([k for k in values.keys()]).strip() 
        vals_filler = '(%s)' % ', '.join(['%s' for _ in values.keys()]).strip() 
        
        cmd = re.sub('__COLS_PLACEHOLDER__', cols_filler, cmd)
        cmd = re.sub('__VALS_PLACEHOLDER__', vals_filler, cmd)
        
        args = tuple([v for k, v in values.items()])
        
        return cmd, args

    def __check_usr_nick(self, values):
        nick = values.get('usr_nick')

        self.cursor.execute(
            'SELECT usr_nick FROM Users WHERE usr_nick = %s',
            tuple([nick])
        )

        nick_exists = self.cursor.fetchall()

        if nick_exists:
            raise UserExistsError('user with this nick already exists')
    
    def __write(self, cmd, args):
        self.cursor.execute(cmd, args)
    
    def write(self, op, values):
        if op == 'usr_write':
            self.__check_usr_nick(values)
        
        cmd, args = self.__parse_write_expression(op, values)
        
        return self.__write(cmd, args)

    def __delete(self, op, values):
        if op == 'msg_delete':
            self.cursor.execute(
                'DELETE FROM Messages WHERE msg_id = %s;',
                tuple([values['_id']])
            )

        elif op == 'delusr_delete':
            self.cursor.execute(
                'DELETE FROM DelUsers WHERE usr_id = %s;',
                tuple([values['_id']])
            )

        else:
            self.cursor.execute(
                'SELECT * FROM Users WHERE usr_id = %s;',
                tuple([values['_id']])
            )

            fetched_user = list(self.cursor.fetchone())

            # set `active` value

            fetched_user[-1] = 0
            fetched_user = tuple(fetched_user)

            self.write(
                'delusr_write',
                {k: v for k, v in zip(['usr_id', 'usr_nick', 'usr_name', 'usr_bio', 'usr_active'], fetched_user)}
            )

            self.cursor.execute(
                'DELETE FROM Users WHERE usr_id = %s;',
                tuple([values['_id']])
            )

    def delete(self, op, values):
        return self.__delete(op, values)

    def __update(self, op, values):
        if len(values) < 2:
            return

        if values.get('usr_nick') is not None:
            self.__check_usr_nick({'usr_nick': values['usr_nick']})

        cmd = self.UPDATE_CMD_TEMPLATE
        args = list()

        set_filler = ', '.join(['%s = %s' % (k, '%s') for k in values if k != 'usr_id']).strip()
        args.extend([v for k, v in values.items() if k != 'usr_id'] + [values['usr_id']])

        if op == 'usr_update':
            cmd = re.sub('__TABLE_PLACEHOLDER__', 'Users', cmd)
            cmd = re.sub('__SET_PLACEHOLDER__', set_filler, cmd)

            self.cursor.execute(cmd, args)

            if values.get('usr_active') == '0':
                self.delete('usr_delete', {'_id': values['usr_id']})   
        
        else:
            cmd = re.sub('__TABLE_PLACEHOLDER__', 'DelUsers', cmd)
            cmd = re.sub('__SET_PLACEHOLDER__', set_filler, cmd)

            self.cursor.execute(cmd, args)

            if values.get('usr_active') == '1':
                self.__restore_user(values['usr_id'])

    def __restore_user(self, _id):
        self.cursor.execute(
                'SELECT * FROM DelUsers WHERE usr_id = %s;',
                tuple([_id])
            )

        fetched_user = list(self.cursor.fetchone())

        self.__check_usr_nick({'usr_nick': fetched_user[1]})

        self.write(
            'usr_write',
            {k: v for k, v in zip(['usr_nick', 'usr_name', 'usr_bio', 'usr_active'], fetched_user[1:])}
        )


    def update(self, op, values):
        return self.__update(op, values)


if __name__ == '__main__':
    _db = DB(DBNAME, PASSWORD)

    try:
        _db.create_tables()
        _db.fill_dummies()
        _db.commit()
    
    except:
        pass
