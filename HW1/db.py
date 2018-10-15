import os
import re
import sqlite3


class FLDB:
    """
    Freelancing DB
    """
    
    def __init__(self, path):
        self.con = sqlite3.connect(path, check_same_thread=False)
        self.cursor = self.con.cursor()
        
        self.TABLE_PREFIX_MAP = {'Projects': 'prj',
                                 'Freelancers': 'frl',
                                 'Employees': 'emp'
                                }
        
    def create_tables(self):
        self.cursor.execute(
        """
        CREATE TABLE Projects (prj_id INTEGER PRIMARY KEY AUTOINCREMENT,
                               prj_Name TEXT,
                               prj_Wage REAL,
                               prj_Field TEXT,
                               prj_Requirements TEXT,
                               prj_Description TEXT,
                               prj_Due TEXT,
                               prj_EmployeeId INTEGER,
                               prj_FreelancerId INTEGER
                              );
        """
                            )
        
        self.cursor.execute(
        """
        CREATE TABLE Freelancers (frl_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  frl_Name TEXT,
                                  frl_Field TEXT,
                                  frl_Skills TEXT,
                                  frl_Experience TEXT,
                                  frl_ProjectId INTEGER
                                 );
        """
                            )
        
        self.cursor.execute(
        """
        CREATE TABLE Employees (emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                emp_Name TEXT,
                                emp_Field TEXT,
                                emp_ProjectId INTEGER
                               );
        """
                            )
        
    def write_dummies(self):
        records = \
        [
            ('Projects', {'Name': 'Automatic text generation', 'Wage': 100.0, 'Field': 'CS, NLP',
                          'Requirements': 'Hands-on ML experience', 'Description': 'Building RNN based text generation model',
                          'Due': '2018-12-31', 'EmployeeId': 1, 'FreelancerId': -1
                         }
            ),
            ('Projects', {'Name': 'Music video render', 'Wage': 90.0, 'Field': '3d design',
                          'Requirements': 'Exp. with any rendering software', 'Description': 'Rendering futuristic music video',
                          'Due': '2019-01-01', 'EmployeeId': 2, 'FreelancerId': -1
                         }
            ),
            ('Freelancers', {'Name': 'Michael M.', 'Field': 'CS, ML', 'Skills': 'Strong math, ML, neural nets',
                             'Experience': 'Junior data scientist', 'ProjectId': -1
                            }
            ),
            ('Freelancers', {'Name': 'James S.', 'Field': 'CGI', 'Skills': 'CGI, C4D',
                             'Experience': 'C4D for 5 years', 'ProjectId': -1
                            }
            ),
            ('Employees', {'Name': 'LangLearn', 'Field': 'CS, NLP', 'ProjectId': 1}),
            ('Employees', {'Name': 'RenderStuidos', 'Field': 'Graphic design', 'ProjectId': 2})
        ]
        
        for record in records:
            self.write(*record)
        self.commit()
        
    def commit(self):
        self.con.commit()
        
    def close(self):
        self.con.close()
    
    def fetch_dicts(self):
        data = self.cursor.fetchall()
        res = list()
        
        for record in data:
            d = dict()
            
            for idx, col in enumerate(self.cursor.description):
                d[col[0]] = record[idx]
                
            d = {'_'.join(k.split('_')[1:]): v for k, v in d.items()}
            
            res.append(d)
        
        return res
    
    def remove(self, table, _id):
        table = table.capitalize()
        prefix = self.TABLE_PREFIX_MAP[table]
        
        try:
            fetched = self.select_from('*', table, '"%s_id" = "%s"' % (prefix, _id))[0]
        
        # fetched empty
        except IndexError:
            return
        
        cmd = 'DELETE FROM %s WHERE "%s_id" = "%s";' % (table, prefix, _id)
        self.cursor.execute(cmd)
        
        if table == 'Projects':
            frl_id = fetched['FreelancerId']
            emp_id = fetched['EmployeeId']
            self.update('Freelancers', {'ProjectId': -1}, {'id': frl_id})
            self.update('Employees', {'ProjectId': -1}, {'id': emp_id})
        
        elif table == 'Freelancers':
            prj_id = fetched['ProjectId']
            self.update('Projects', {'FreelancerId': -1}, {'id': prj_id})
        
        else:
            prj_id = fetched['ProjectId']
            if prj_id > 0:
                self.remove('Projects', prj_id)
           
    def insert_into(self, into, keys, vals):
        cmd = 'INSERT INTO %s %s VALUES %s;' % (into, keys, vals)
        self.cursor.execute(cmd)

    def select_from(self, what, _from, where):
        cmd = 'SELECT %s FROM %s WHERE %s;' % (what, _from, where)
        self.cursor.execute(cmd)
        return self.fetch_dicts()

    def update(self, table, _set, where):
        table = table.capitalize()
        prefix = self.TABLE_PREFIX_MAP[table]
        _set = '%s' % ', '.join(['"%s_%s" = "%s"' % (prefix, k, v) for k, v in _set.items()])
        where = '%s' % ', '.join(['"%s_%s" = "%s"' % (prefix, k, v) for k, v in where.items()])
        cmd = "UPDATE %s SET %s WHERE %s;" % (table, _set, where)
        self.cursor.execute(cmd)
    
    def assign_project(self, prj_id, frl_id):
        self.update('Projects', {'FreelancerId': frl_id}, {'id': prj_id})
        self.update('Freelancers', {'ProjectId': prj_id}, {'id': frl_id})
        
    def cancel_project(self, prj_id, frl_id):
        self.update('Projects', {'FreelancerId': -1}, {'id': prj_id})
        self.update('Freelancers', {'ProjectId': -1}, {'id': frl_id})
        
    def fetch_all(self, table):
        table = table.capitalize()
        cmd = 'SELECT * FROM %s;' % table
        self.cursor.execute(cmd)
        return self.fetch_dicts()
    
    def write(self, table, values):
        table = table.capitalize()
        prefix = self.TABLE_PREFIX_MAP[table]
        keys = '(%s)' % ', '.join(['"%s_%s"' % (prefix, k) for k in values])
        vals = '(%s)' % ', '.join(['"%s"' % values[k] for k in values])
        self.insert_into(table, keys, vals)
    
    def read(self, table, values):
        table = table.capitalize()
        where = list()
        prefix = self.TABLE_PREFIX_MAP[table]
        
        for attribute, query in values.items():
            if query:
                where.append(self.parse_query('%s_%s' % (prefix, attribute), query))
        
        return self.select_from('*', table, 'AND'.join(where))
    
    def parse_query(self, attribute, query):
        query = str(query)
        args = self.parse_args(attribute, query)
        ops = self.parse_ops(query)

        if not ops:
            return ' '.join(args)

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

        return ' '.join(res)
    
    def parse_args(self, attribute, query):
        args = list()
        args_raw = re.split('[&|\|]', query)

        for arg_raw in args_raw:
            arg_raw = arg_raw.strip()

            if '%' in arg_raw or '_' in arg_raw:
                arg = '"%s" LIKE "%s"' % (attribute, re.sub('[\(\)]', '', arg_raw))

            else:
                arg = '"%s" = "%s"' % (attribute, re.sub('[\(\)]', '', arg_raw))

            if arg_raw.startswith('('):
                arg = '(' * arg_raw.count('(') + arg

            if arg_raw.endswith(')'):
                arg += ')' * arg_raw.count(')')

            args.append(arg)

        return args
    
    def parse_ops(self, query):
        ops = re.sub('[^&|]', ' ', query)
        ops = re.sub(' +', ' ', ops)
        ops = ops.strip()
        ops = ops.split()
        ops = list(map(lambda x: 'AND' if x == '&' else 'OR', ops))
        return ops

if __name__ == '__main__':
    fldb = FLDB('fldb.db')
    
    try:
        fldb.create_tables()
        fldb.write_dummies()
    
    except:
        pass

    finally:
        fldb.con.close()
        