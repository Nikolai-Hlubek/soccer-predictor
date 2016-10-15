import requests
import bs4
import time
import json


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


url = 'http://www.11v11.com/matches/iceland-v-turkey-09-september-2014-310334'

def scrape_team(h):
    idx = 0
    team = h[idx].find_all('a')[0].text
    score = float(h[idx].find_all('span')[0].text)

    idx += 1
    scorers = []
    if h[idx].find_all("h4")[0].text == 'Goals:':
        scorers_raw = h[idx].find_all("tr")
        for sr in scorers_raw:
            name = sr.find_all("td")[0].text
            time = float(sr.find_all("td")[2].text)
            scorers.append({'name' : name, 'time' : time})
        idx += 1

        print(scorers)

    start_players_raw = h[idx].find_all("div", class_="player")
    start_players = []
    for sp in start_players_raw:
        if len(sp.find_all("span")) > 0:
            pos = sp.find_all("span")[0].text
        else:
            pos = 'NA'
        name = sp.find_all("a")[0].text
        if name[0] == ' ':
            name = name[1:]
        start_players.append({'name' : name, 'pos' : pos})
    idx += 1

    print(start_players)

    sub_players = []
    if h[idx].find_all("h4")[0].text == 'Substitutions:':
        sub_players_in_raw = h[idx].find_all("span", class_="substitute")
        sub_players_out_raw = h[idx].find_all("span", class_="substituted")
        for i in range(len(sub_players_in_raw)):
            sub_in = sub_players_in_raw[i].text
            sub_in = sub_in.replace('\t', '')
            sub_in = sub_in.replace('\n', '')
            sub_out = sub_players_out_raw[i].text
            sub_out = sub_out.replace('\t', '')
            sub_out = sub_out.replace('\n', '')
            sub_players.append({'sub in' : sub_in, 'sub out' : sub_out})
        idx += 1

        print(sub_players)

    bench_players_raw = h[-1].find_all("div", class_="player")
    bench_players = []
    for bp in bench_players_raw:
        if len(bp.find_all("span")) > 0:
            pos = bp.find_all("span")[0].text
        else:
            pos = 'NA'
        name = bp.find_all("a")[0].text
        if name[0] == ' ':
            name = name[1:]
        bench_players.append({'name' : name, 'pos' : pos})
    print(bench_players)

    res = {}
    res['team'] = team
    res['score'] = score
    res['scorers'] = scorers
    res['start'] = start_players
    res['sub'] = sub_players
    res['bench'] = bench_players

    return res


def scrape_game_11v11(url):
    r = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(r.content, 'html.parser')

    home = scrape_team( soup.find_all("div", class_="home") )
    away = scrape_team( soup.find_all("div", class_="away") )

    res = {}
    res['home'] = home
    res['away'] = away

    return res


quali = []

url_base = 'http://www.11v11.com'
url = 'http://www.11v11.com/competitions/uefa-european-championship/2016/qualifying/'
r = requests.get(url, headers=headers)
soup = bs4.BeautifulSoup(r.content, 'html.parser')
games = soup.find_all('a')[20:-9]
for game in games:
    query_url = url_base + game['href']
    print(query_url)
    quali.append( scrape_game_11v11(query_url) )


with open('qualifier_1.json', 'w') as outfile:
    json.dump(quali, outfile)

