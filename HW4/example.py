from db import HOST, PORT, DB


db = DB(HOST, PORT)

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
    print('%s -> %s' % (it_word, db.transcript(it_word, 'it', 'ru')))
    