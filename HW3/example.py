from db import DB, DBNAME, PASSWORD


_db = DB(DBNAME, PASSWORD)


IT_WORDS = [
    'i',
    'il',
    'li',
    'lei',
    'gli',
    'aglio',
    'cielo',
    'collo',
    'casa',
    'suo',
    'cassa',
    'ho', 
]


for it_word in IT_WORDS:
    print('%s -> %s' % (it_word, _db.transcript(it_word, 'it', 'ru')))
    
