import json
import logging

import ScrapeTransfermarkt

logging.basicConfig( )
logging.getLogger("ScrapeTransfermarkt").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.DEBUG)

names_transfermarkt = {'Hannes Halldorsson' : 'Hannes Thór Halldórsson',
                       'Ersun Gulum' : 'Ersan Gülüm',
                       'Burak Yilmaz' : 'Burak Yilmaz',
                       'Omer Toprak' : 'Ömer Toprak',
                       'Birkir Saevarsson' : 'Birkir Már Saevarsson',
                       'Ogmundur Kristinsson' : 'Ögmundur Kristinsson',
                       'Senar Ozbayrakli' : 'Sener Özbayrakli',
                       'Sergei Khizhnichenko' : 'Sergey Khizhnichenko',
                       'Tanat Nusserbayev' : 'Tanat Nuserbayev',
                       'Gafurzhan Suyimbaev' : 'Gafurzhan Suyumbayev',
                       'Dmitriy Shomko' : 'Dmitri Shomko',
                       'Sergei Maliy' : 'Sergiy Maly',
                       'Theodhor Gebre Selassie' : 'Theodor Gebre Selassie',
                       'Klaas Jan Huntelaar' : 'Klaas-Jan Huntelaar',
                       'Ulan Konysbaev' : 'Ulan Konysbayev',
                       'Ladislav Krejci' : 'Ladislav Krejcí',
                       'Igor Tarasovs' : 'Igors Tarasovs',
                       'Bauyrzhan Dzholchiev' : 'Bauyrzhan Dzholchiyev',
                       'Mark Gorman' : 'Rhys Gorman',
                       'Rinat Abdulin' : 'Renat Abdulin',
                       'Andrei Sidelnikov' : 'Andrey Sidelnikov',
                       'Ilia Vorotnikov' : 'Ilya Vorotnikov',
                       'Alex Kolinko' : 'Aleksandrs Kolinko',
                       'Andrei Karpovich' : 'Andrey Karpovich',
                       'Ritvars  Rugins' : 'Ritvars Rugins',
                       'Josep Manuel Ayala' : 'José Ayala',
                       'Ildefonso Solo Lima' : 'Ildefons Lima',
                       'Eduaedo Peppe' : 'Carlos Edu Peppe',
                       'Marc Valez' : 'Marc Vales',
                       'Ivan Lorenzo' : 'Iván Lorenzo',
                       'Charis Kyriakou' : 'Charalampos Kyriakou',
                       'Georgos Merkis' : 'Giorgos Merkis',
                       'Konstantinos Makrides' : 'Konstantinos Makridis',
                       'Demetris Christofi' : 'Dimitris Christofi',
                       'Jonny Williams' : 'Jonathan Williams',
                       'Marcio Vieira' : 'Márcio Vieira',
                       'Kostas Charalambides' : 'Konstantinos Charalampidis',
                       'Antreas Makris' : 'Andreas Makris',
                       'Eytan Tibi' : 'Eitan Tibi',
                       'Tal Ben Haim II' : 'Tal Ben Haim',
                       'George C Williams' : 'George Williams',
                       'Pieros Soteriou' : 'Pieros Sotiriou',
                       'Dave Cotterill' : 'David Cotterill',
                       'James M Collins' : 'James Collins',
                       'Sebastian Gomez' : 'Sebastián Gómez',
                       'Milan Duric' : 'Milan Djuric',
                       'Kostas Laifes' : 'Konstantinos Laifis',
                       'Elazar Dasa' : 'Eli Dasa',
                       'Moanes Dabour' : 'Munas Dabbur',
                       'Cristian Martinez' : 'Cristian Martínez',
                       'Beram Kayal' : 'Biram Kayal',


        }


def add_worth_pos(p):
    name = p['name']
    if name in names_transfermarkt:
        name = names_transfermarkt[name]
        print('---', name)
    (success, worth, pos) = ScrapeTransfermarkt.query_transfermarkt( name )
    if success:
        p['worth'] = worth
        p['pos'] = pos
    else:
        logger.debug('{} --- {}'.format(p['name'], 'Problem'))


def main():
    with open('qualifier_1.json', 'r') as infile:
        data = json.load(infile)


    for ctr,d in enumerate(data):
        logger.info('Game Nr: {}'.format(ctr))
        if ctr < 60:
            continue
        if ctr == 90:
            break

        t1 = d['away']['team']
        r1 = d['away']['score']
        t2 = d['home']['team']
        r2 = d['home']['score']
        
        logger.info('{} vs {}'.format(t1,t2))

        for p in d['home']['start']:
            add_worth_pos(p)
        for p in d['away']['start']:
            add_worth_pos(p)

    with open('qualifier_2.json', 'w') as outfile:
        json.dump(data, outfile)

if __name__ == '__main__':
    main()
