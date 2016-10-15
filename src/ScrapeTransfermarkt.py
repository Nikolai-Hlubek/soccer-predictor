import requests
import bs4
import time
import logging


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

logging.getLogger("requests").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def query_transfermarkt(name):

    name_query = name.replace(' ', '+')    # Exchange whitespace for query
    
    query_str = 'http://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={}&x=0&y=0'.format(name_query)
    r = requests.get(query_str, headers=headers)

    soup = bs4.BeautifulSoup(r.content, 'html.parser')
    worth_str = soup.find_all('td', class_='rechts hauptlink')
    logger.info(worth_str)
    player_found = False

    if len(worth_str) == 1:
        player_found = True
    elif len(worth_str) > 1:
         a = soup.find_all('table', class_="inline-table")[0]
         b = a.find_all('a', class_="spielprofil_tooltip")[0]
         if b.text == name:
             player_found = True

    if player_found:
        worth_str = worth_str[0].text

        if ' Mill. €' in worth_str:
            worth_str = worth_str.replace(' Mill. €', '')
            worth_str = worth_str.replace(',', '.')
            worth = float(worth_str)
        elif ' Th. €' in worth_str:
            worth_str = worth_str.replace(' Th. €', '')
            worth_str = worth_str.replace(',', '.')
            worth = float(worth_str) / 1000
        elif '-' == worth_str:
            worth = None


        pos = soup.find_all('td', class_="zentriert")[0].text

        logger.info('{},{}'.format(name, worth))
    else:
        worth = None
        pos = None

    return(player_found, worth, pos)


def main():
    f = open('EM2016-PlayersNetWorth.csv')
    g = open('EM2016-PlayersNetWorth_new.csv', 'w')

    g.write('EM2016 Players,Net Worth in Millions\n')

    not_found = []

    line = f.readline()   # Header
    line = f.readline()   # Initial for while loop
    while line != '':
        if line[-1] == '\n':
            line = line[:-1]
        name = line.split(',')
        name = name[0]                   # Only player
        
        (success, worth, pos) = query_transfermarkt(name)
        if success:
            g.write('{},{}\n'.format(name, worth))
        else:
            not_found.append(name)

        line = f.readline()
        time.sleep(0.1)              # Pretend human speed

    print('Problem with the following names: ')
    print(not_found)

    f.close()
    g.close()


if __name__ == '__main__':
    main()
