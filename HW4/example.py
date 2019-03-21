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

# i -> и
# il -> иль
# li -> ли
# lei -> лей
# gli -> ли
# aglio -> альйо
# cielo -> чиело
# collo -> колло
# casa -> каза
# suo -> суо
# cassa -> касса
# ho -> о

