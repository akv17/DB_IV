import re

import pymongo


HOST = 'localhost'
PORT = 27017


class DB:
    
    def __init__(self, host, port, db_name='transcription'):
        self.host = host
        self.port = port
        self.db_name = db_name
        
        self.COLLECTIONS_NAMES = ('phonemes', 'rules')
        self.INDEX_NAMES = ('phon_id', 'rule_id')
        self.PHONEME_PARSERS = {'it': self.phoneme_parser_it}
        
        self.client = pymongo.MongoClient(self.host, self.port)
        self.db = self.client[self.db_name]
        self.collections = {col: self.db[col] for col in self.COLLECTIONS_NAMES}

    def create_index(self):
        for idx_name, col_name in zip(self.INDEX_NAMES, self.COLLECTIONS_NAMES):
            self.collections[col_name].create_index([(idx_name, pymongo.ASCENDING)], unique=True)
            
    def drop_collections(self):
        for col_name in self.COLLECTIONS_NAMES:
            self.db.drop_collection(col_name)

    def fill_collections(self):
        self.collections['phonemes'].insert_many(
            (
                {'phon_id': 1, 'phon_char': 'i', 'lang': 'it', 'features': '-cons;+front'},
                {'phon_id': 2, 'phon_char': 'и', 'lang': 'ru', 'features': '-cons;+front'},
                {'phon_id': 3, 'phon_char': 'e', 'lang': 'it', 'features': '-cons;+front'},
                {'phon_id': 4, 'phon_char': 'е', 'lang': 'ru', 'features': '-cons;+front'},
                {'phon_id': 5, 'phon_char': 'a', 'lang': 'it', 'features': '-cons;-front'},
                {'phon_id': 6, 'phon_char': 'а', 'lang': 'ru', 'features': '-cons;-front'},
                {'phon_id': 7, 'phon_char': 'o', 'lang': 'it', 'features': '-cons;-front'},
                {'phon_id': 8, 'phon_char': 'о', 'lang': 'ru', 'features': '-cons;-front'},
                {'phon_id': 9, 'phon_char': 'u', 'lang': 'it', 'features': '-cons;-front'},
                {'phon_id': 10, 'phon_char': 'у', 'lang': 'ru', 'features': '-cons;-front'},
                {'phon_id': 11, 'phon_char': 'c', 'lang': 'it', 'features': '+cons;+stop'},
                {'phon_id': 12, 'phon_char': 'к', 'lang': 'ru', 'features': '+cons;+stop;-voice'},
                {'phon_id': 13, 'phon_char': 'ч', 'lang': 'ru', 'features': '+cons;+stop;+fric;-voice'},
                {'phon_id': 14, 'phon_char': 'l', 'lang': 'it', 'features': '+cons;+son;-rounded'},
                {'phon_id': 15, 'phon_char': 'л', 'lang': 'ru', 'features': '+cons;+son'},
                {'phon_id': 16, 'phon_char': 's', 'lang': 'it', 'features': '+cons;+fric'},
                {'phon_id': 17, 'phon_char': 'с', 'lang': 'ru', 'features': '+cons;+fric;-voice'},
                {'phon_id': 18, 'phon_char': 'з', 'lang': 'ru', 'features': '+cons;+fric;+voice'},
                {'phon_id': 19, 'phon_char': 'gl', 'lang': 'it', 'features': '+cons;+son;+front'},
                {'phon_id': 20, 'phon_char': '^', 'lang': 'it', 'features': 'START'},
                {'phon_id': 21, 'phon_char': '#', 'lang': 'it', 'features': 'END'},
                {'phon_id': 22, 'phon_char': 'й', 'lang': 'ru', 'features': '+cons;+son'},
                {'phon_id': 23, 'phon_char': 'ль', 'lang': 'ru', 'features': '+cons;+son;+front'},
            )
        )
        
        self.collections['rules'].insert_many(
            (
                {
                    'rule_id': 1,
                    'lang': ['it','ru'],
                    'phon_ids': [1, 2]
                },
                {
                    'rule_id': 2,
                    'lang': ['it','ru'],
                    'phon_ids': [3, 4]
                },
                {
                    'rule_id': 3,
                    'lang': ['it','ru'],
                    'phon_ids': [5, 6]
                },
                {
                    'rule_id': 4,
                    'lang': ['it','ru'],
                    'phon_ids': [7, 8]
                },
                {
                    'rule_id': 5,
                    'lang': ['it','ru'],
                    'phon_ids': [9, 10]
                },
                {
                    'rule_id': 6,
                    'lang': ['it','ru'],
                    'phon_ids': [14, 15]
                },
                {
                    'rule_id': 7,
                    'lang': ['it','ru'],
                    'phon_ids': [20, 8]
                },
                {
                    'rule_id': 8,
                    'lang': ['it','ru'],
                    'phon_ids': [16, 17]
                },
                {
                    'rule_id': 9,
                    'lang': ['it','ru'],
                    'phon_ids': [19, 23]
                },
                {
                    'rule_id': 10,
                    'lang': ['it','ru'],
                    'phon_ids': [11, 13],
                    'context_features': {'ri': '-cons;+front'}
                },
                {
                    'rule_id': 11,
                    'lang': ['it','ru'],
                    'phon_ids': [11, 12],
                    'context_features': {'ri': '-cons;-front'}
                },
                {
                    'rule_id': 12,
                    'lang': ['it','ru'],
                    'phon_ids': [14, 23],
                    'context_features': {'ri': 'END'}
                },
                {
                    'rule_id': 13,
                    'lang': ['it','ru'],
                    'phon_ids': [19, 15],
                    'context_features': {'le': 'START'}
                },
                {
                    'rule_id': 14,
                    'lang': ['it','ru'],
                    'phon_ids': [16, 18],
                    'context_features': {'le': '-cons;+front', 'ri': '-cons;+front'}
                },
                {
                    'rule_id': 15,
                    'lang': ['it','ru'],
                    'phon_ids': [16, 18],
                    'context_features': {'le': '-cons;+front', 'ri': '-cons;-front'}
                },
                {
                    'rule_id': 16,
                    'lang': ['it','ru'],
                    'phon_ids': [16, 18],
                    'context_features': {'le': '-cons;-front', 'ri': '-cons;+front'}
                },
                {
                    'rule_id': 17,
                    'lang': ['it','ru'],
                    'phon_ids': [16, 18],
                    'context_features': {'le': '-cons;-front', 'ri': '-cons;-front'}
                },
                {
                    'rule_id': 18,
                    'lang': ['it','ru'],
                    'phon_ids': [1, 22],
                    'context_features': {'le': '-cons;+front', 'ri': 'END'}
                },
                {
                    'rule_id': 19,
                    'lang': ['it','ru'],
                    'phon_ids': [1, 22],
                    'context_features': {'le': '-cons;-front', 'ri': 'END'}
                },
                {
                    'rule_id': 20,
                    'lang': ['it','ru'],
                    'phon_ids': [1, 22],
                    'context_features': {'le': '+cons;+son;+front', 'ri': '-cons;+front'}
                },
                {
                    'rule_id': 21,
                    'lang': ['it','ru'],
                    'phon_ids': [1, 22],
                    'context_features': {'le': '+cons;+son;+front', 'ri': '-cons;-front'}
                }
                
            )
        )
                
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

    def get_transcription(self, query):
        """
        query: langs, target_char, le_char, ri_char
        """
        
        sc_phon_id = self.db.phonemes.find_one(
            {'phon_char': query['target_char'], 'lang': query['langs'][0]}
        )['phon_id']
        
        le_features = self.db.phonemes.find_one(
            {'phon_char': query['le_char'], 'lang': query['langs'][0]}
        )['features']
        
        ri_features = self.db.phonemes.find_one(
            {'phon_char': query['ri_char'], 'lang': query['langs'][0]}
        )['features']
        
        queries_chain = [
            {
                'lang': query['langs'],
                'phon_ids.0': sc_phon_id,
                'context_features': {'le': le_features, 'ri': ri_features}
            },
            {
                'lang': query['langs'],
                'phon_ids.0': sc_phon_id,
                'context_features': {'ri': ri_features}
            },
            {
                'lang': query['langs'],
                'phon_ids.0': sc_phon_id,
                'context_features': {'le': le_features}
            },
            {
                'lang': query['langs'],
                'phon_ids.0': sc_phon_id
            }
        ]
        
        for _query in queries_chain:
            rule = self.db.rules.find_one(_query)
            
            if rule is not None:
                tr_phon_char = self.db.phonemes.find_one(
                    {'phon_id': rule['phon_ids'][1], 'lang': query['langs'][1]}
                )['phon_char']
                
                return tr_phon_char

    def transcript(self, word, from_lang, to_lang):
        query = {
            'langs': [from_lang, to_lang],
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
            query.update(
                {
                    'target_char': phon,
                    'le_char': phonemes[idx-1],
                    'ri_char': phonemes[idx+1]
                }
            )

            transcripted += self.get_transcription(query)
            idx += 1

        return transcripted
