import re
import psycopg2


DBNAME = 'transcript'
PASSWORD = 'testpassword1010'


class DB:

    def __init__(self, dbname, password):
        self.dbname = dbname

        self.conn = psycopg2.connect(dbname=dbname,
                                     password=password,
                                     user='postgres',
                                     host='localhost',
                                     port=5432,
        )

        self.cursor = self.conn.cursor()

        self.TABLE_PRECEDENCE = ('BiDepRules', 'RiDepRules', 'LeDepRules', 'IndepRules')
        self.PHONEME_PARSERS = {'it': self.phoneme_parser_it}

        self.init_statements()

    def init_statements(self):
        self.STATEMENTS = {
            'IndepRules': \
            """
            SELECT
            (SELECT phon_char FROM Phonemes WHERE phon_id = sc_phon_id and lang = %s),
            (SELECT phon_char FROM Phonemes WHERE phon_id = tr_phon_id and lang = %s)
            FROM IndepRules
            WHERE
            sc_phon_id = (SELECT phon_id from Phonemes WHERE phon_char = %s AND lang = %s)
            AND
            tr_lang = %s;
            """,

            'RiDepRules': \
            """
            SELECT
                (SELECT phon_char FROM Phonemes WHERE phon_id = sc_phon_id and lang = %s),
                (SELECT phon_char FROM Phonemes WHERE phon_id = tr_phon_id and lang = %s)
            FROM RiDepRules
            WHERE
            sc_phon_id = (
                SELECT phon_id from Phonemes WHERE phon_char = %s AND lang = %s)
            AND
            ri_context_features = (
                SELECT features FROM PhoneticFeatures WHERE phon_id =
                    (SELECT phon_id FROM Phonemes WHERE phon_char = %s and lang = %s)
            )
            AND
            tr_lang = %s;
            """,

            'LeDepRules': \
            """
            SELECT
                (SELECT phon_char FROM Phonemes WHERE phon_id = sc_phon_id and lang = %s),
                (SELECT phon_char FROM Phonemes WHERE phon_id = tr_phon_id and lang = %s)
            FROM LeDepRules
            WHERE
            sc_phon_id = (
                SELECT phon_id from Phonemes WHERE phon_char = %s AND lang = %s)
            AND
            le_context_features = (
                SELECT features FROM PhoneticFeatures WHERE phon_id =
                    (SELECT phon_id FROM Phonemes WHERE phon_char = %s and lang = %s)
            )
            AND
            tr_lang = %s;
            """,

            'BiDepRules': \
            """
            SELECT
                (SELECT phon_char FROM Phonemes WHERE phon_id = sc_phon_id and lang = %s),
                (SELECT phon_char FROM Phonemes WHERE phon_id = tr_phon_id and lang = %s)
            FROM BiDepRules
            WHERE
            sc_phon_id = (
                SELECT phon_id from Phonemes WHERE phon_char = %s AND lang = %s)
            AND
            ri_context_features = (
                SELECT features FROM PhoneticFeatures WHERE phon_id =
                    (SELECT phon_id FROM Phonemes WHERE phon_char = %s and lang = %s)
            )
            AND
            le_context_features = (
                SELECT features FROM PhoneticFeatures WHERE phon_id =
                    (SELECT phon_id FROM Phonemes WHERE phon_char = %s and lang = %s)
            )
            AND
            tr_lang = %s;
            """

        }

        self.ARG_TEMPLATES = {
            'IndepRules': ('sc_lang', 'tr_lang',
                           'target_char', 'sc_lang',
                           'tr_lang'),

            'RiDepRules': ('sc_lang', 'tr_lang',
                           'target_char', 'sc_lang',
                           'ri_char', 'sc_lang',
                           'tr_lang'),

            'LeDepRules': ('sc_lang', 'tr_lang',
                           'target_char', 'sc_lang',
                           'le_char', 'sc_lang',
                           'tr_lang'),

            'BiDepRules': ('sc_lang', 'tr_lang',
                           'target_char', 'sc_lang',
                           'ri_char', 'sc_lang',
                           'le_char', 'sc_lang',
                           'tr_lang'),

        }

    def create_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE Phonemes (
                phon_id INTEGER PRIMARY KEY,
                phon_char TEXT,
                lang TEXT  
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE PhoneticFeatures (
                phon_id INTEGER PRIMARY KEY,
                features TEXT
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IndepRules (
                rule_id INTEGER PRIMARY KEY,
                sc_lang TEXT,
                tr_lang TEXT,
                sc_phon_id INTEGER,
                tr_phon_id INTEGER
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE RiDepRules (
                rule_id INTEGER PRIMARY KEY,
                sc_lang TEXT,
                tr_lang TEXT,
                sc_phon_id INTEGER,
                tr_phon_id INTEGER,
                ri_context_features TEXT
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE LeDepRules (
                rule_id INTEGER PRIMARY KEY,
                sc_lang TEXT,
                tr_lang TEXT,
                sc_phon_id INTEGER,
                tr_phon_id INTEGER,
                le_context_features TEXT
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE BiDepRules (
                rule_id INTEGER PRIMARY KEY,
                sc_lang TEXT,
                tr_lang TEXT,
                sc_phon_id INTEGER,
                tr_phon_id INTEGER,
                le_context_features TEXT,
                ri_context_features TEXT
            )
            """
        )

        self.conn.commit()

    def drop_tables(self):
        self.cursor.execute('DROP TABLE Phonemes')
        self.cursor.execute('DROP TABLE PhoneticFeatures')
        self.cursor.execute('DROP TABLE IndepRules')
        self.cursor.execute('DROP TABLE RiDepRules')
        self.cursor.execute('DROP TABLE LeDepRules')
        self.cursor.execute('DROP TABLE BiDepRules')

        self.conn.commit()

    def fill_tables(self):
        self.cursor.execute(
            """
            INSERT INTO Phonemes
            VALUES 
                (1, 'i', 'it'),
                (2, 'и', 'ru'),
                (3, 'e', 'it'),
                (4, 'е', 'ru'),
                (5, 'a', 'it'),
                (6, 'а', 'ru'),
                (7, 'o', 'it'),
                (8, 'о', 'ru'),
                (9, 'u', 'it'),
                (10, 'у', 'ru'),
                (11, 'c', 'it'),
                (12, 'к', 'ru'),
                (13, 'ч', 'ru'),
                (14, 'l', 'it'),
                (15, 'л', 'ru'),
                (16, 's', 'it'),
                (17, 'с', 'ru'),
                (18, 'з', 'ru'),
                (19, 'gl', 'it'),
                (20, '^', 'it'),
                (21, '#', 'it'),
                (22, 'й', 'ru'),
                (23, 'ль', 'ru')
            """
        )

        self.cursor.execute(
            """
            INSERT INTO PhoneticFeatures
            VALUES
                (1, '-cons;+front'),
                (2, '-cons;+front'),
                (3, '-cons;+front'),
                (4, '-cons;+front'),
                (5, '-cons;-front'),
                (6, '-cons;-front'),
                (7, '-cons;-front'),
                (8, '-cons;-front'),
                (9, '-cons;-front'),
                (10, '-cons;-front'),
                (11, '+cons;+stop'),
                (12, '+cons;+stop;-voice'),
                (13, '+cons;+stop;+fric;-voice'),
                (14, '+cons;+son;-rounded'),
                (15, '+cons;+son'),
                (16, '+cons;+fric'),
                (17, '+cons;+fric;-voice'),
                (18, '+cons;+fric;+voice'),
                (19, '+cons;+son;+front'),
                (20, 'START'),
                (21, 'END'),
                (22, '+cons;+son'),
                (23, '+cons;+son;+front')
            """
        )

        self.cursor.execute(
            """
            INSERT INTO IndepRules
            VALUES
                (1, 'it', 'ru', 1, 2),
                (2, 'it', 'ru', 3, 4),
                (3, 'it', 'ru', 5, 6),
                (4, 'it', 'ru', 7, 8),
                (5, 'it', 'ru', 9, 10),
                (6, 'it', 'ru', 14, 15),
                (8, 'it', 'ru', 20, 8),
                (9, 'it', 'ru', 16, 17),
                (10, 'it', 'ru', 19, 23)
            """
        )

        self.cursor.execute(
            """
            INSERT INTO RiDepRules
            VALUES
                (1, 'it', 'ru', 11, 13, '-cons;+front'),
                (2, 'it', 'ru', 11, 12, '-cons;-front'),
                (3, 'it', 'ru', 14, 23, 'END')
            """
        )

        self.cursor.execute(
            """
            INSERT INTO LeDepRules
            VALUES
                (1, 'it', 'ru', 19, 15, 'START')
            """
        )

        self.cursor.execute(
            """
            INSERT INTO BiDepRules
            VALUES
                (1, 'it', 'ru', 16, 18, '-cons;+front', '-cons;+front'),
                (2, 'it', 'ru', 16, 18, '-cons;+front', '-cons;-front'),
                (3, 'it', 'ru', 16, 18, '-cons;-front', '-cons;+front'),
                (4, 'it', 'ru', 16, 18, '-cons;-front', '-cons;-front'),
                (5, 'it', 'ru', 1, 22, '-cons;+front', 'END'),
                (6, 'it', 'ru', 1, 22, '-cons;-front', 'END'),
                (7, 'it', 'ru', 1, 22, '+cons;+son;+front', '-cons;+front'),
                (8, 'it', 'ru', 1, 22, '+cons;+son;+front', '-cons;-front')
            """
        )

        self.conn.commit()

    def phoneme_parser_it(self, word):
        parsed = []

        word = word.replace('h', '')
        word = word.replace('gl', 'L')

        for s in word:
            if s == 'L':
                parsed.append('gl')
            
            else:
                parsed.append(s)

        return parsed

    def get_transcription(self, kwargs):
        """
        kwargs: sc_lang, tr_lang, target_char, le_char, ri_char
        """

        for table in self.TABLE_PRECEDENCE:
            args = tuple([kwargs[k] for k in self.ARG_TEMPLATES[table]])
            self.cursor.execute(self.STATEMENTS[table], args)

            res = self.cursor.fetchone()

            if res:
                return res

    def transcript(self, word, from_lang, to_lang):
        kwargs = {
            'sc_lang': from_lang,
            'tr_lang': to_lang,
            'target_char': '',
            'le_char': '',
            'ri_char': ''
        }
        
        word = word.lower()
        word = re.sub('[\W]', '', word)

        phonemes = self.PHONEME_PARSERS[from_lang](word)
        phonemes = ['^'] + phonemes + ['#']

        transcripted = ''

        idx = 1
        for phon in phonemes[1:-1]:
            kwargs.update(
                {
                    'target_char': phon,
                    'le_char': phonemes[idx-1],
                    'ri_char': phonemes[idx+1]
                }
            )

            transcripted += self.get_transcription(kwargs)[1]
            idx += 1
        
        return transcripted
