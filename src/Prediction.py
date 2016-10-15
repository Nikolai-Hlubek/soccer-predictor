import json
import logging
import random
import math
import heapq

logging.basicConfig(level=logging.WARNING)

#logging.getLogger(__name__).setLevel(logging.INFO)
logger = logging.getLogger(__name__)
#logger.setLevel(logging.ERROR)
logger.setLevel(logging.WARNING)


def worth_goalie(p):
    worth = 0.0
    for pi in p:
        if p[pi] > worth:
            worth = p[pi]
    return worth


def worth_defense(p,n):
    worth = 0.0
    l = []
    for pi in p:
        l.append(p[pi])
    worth = sum(heapq.nlargest(n, l))
    return worth


def worth_midfield(p,n):
    worth = 0.0
    l = []
    for pi in p:
        l.append(p[pi])
    worth = sum(heapq.nlargest(n, l))
    return worth

def worth_attack(p,n):
    worth = 0.0
    l = []
    for pi in p:
        l.append(p[pi])
    worth = sum(heapq.nlargest(n, l))
    return worth


def predict(w, c1, c2, c3, c4, c5, c6):
    zone = 'midfield'
    possession = 'home'
    timer = 90

    score_home = 0
    score_away = 0

    norm1 = w['home']['g'] + w['home']['d'] + w['home']['m'] + w['home']['a']
    norm2 = w['away']['g'] + w['away']['d'] + w['away']['m'] + w['away']['a']
    norm = max(norm1, norm2)

    # home zone home goal
    hgk = w['home']['g']
    hgk /= norm
    # home zone home goal to zone home defense
    hgd = w['home']['d'] + c4 * w['home']['m']
    hgd /= norm
    # home zone home mid to zone away defense
    hmd = w['home']['a'] + w['home']['m'] + c5 * w['home']['d']
    hmd /= norm
    # home zone away defense to zone away goal
    hdg = w['home']['a'] + w['home']['m']
    hdg /= norm
    # home zone away goal
    hgs = w['home']['a'] + c6 * w['home']['m']
    hgs /= norm

    # away zone away goal
    agk = w['away']['g']
    agk /= norm
    # away zone away goal to zone away defense
    agd = w['away']['d'] + c4 * w['away']['m']
    agd /= norm
    # away zone away mid to zone home defense
    amd = w['away']['a'] + w['away']['m'] + c5 * w['away']['d']
    amd /= norm
    # away zone home defense to zone home goal
    adg = w['away']['a'] + w['away']['m']
    adg /= norm
    # away zone home goal
    ags = w['away']['a'] + c6 * w['away']['m']
    ags /= norm


    while timer > 0:
        timer -= 2
#        r1 = random.uniform(-0.5, 0.5)
#        r2 = random.uniform(-0.5, 0.5)
        r1 = random.gauss(0.6, 0.75)
        r2 = random.gauss(0.6, 0.75)

        if zone == 'midfield':
            if possession == 'home':
                m = r1 * hmd - r2 * amd
                logger.debug('h c1 {}'.format(m))
                if m > c1:
                    zone = 'defense away'
                else:
                    zone = 'midfield'
                    possession = 'away'
            elif possession == 'away':
                m = r1 * amd - r2 * hmd
                logger.debug('a c1 {}'.format(m))
                if m > c1:
                    zone = 'defense home'
                else:
                    zone = 'midfield'
                    possession = 'home'
        elif zone == 'defense away':
            if possession == 'home':
                m = r1 * hdg - r2 * adg
                logger.debug('h c2 {}'.format(m))
                if m > c2:
                    zone = 'goal away'
                else:
                    zone = 'midfield'
                    possession = 'away'
        elif zone == 'goal away':
            if possession == 'home':
                m = r1 * hgs - r2 * agk
                logger.debug('h c3 {}'.format(m))
                if m > c3:
                    score_home += 1
                zone = 'midfield'
                possession = 'away'
        elif zone == 'defense home':
            if possession == 'away':
                m = r1 * adg - r2 * hdg
                logger.debug('a c2 {}'.format(m))
                if m > c2:
                    zone = 'goal home'
                else:
                    zone = 'midfield'
                    possession = 'home'
        elif zone == 'goal home':
            if possession == 'away':
                m = r1 * ags - r2 * hgk
                logger.debug('a c3 {}'.format(m))
                if m > c3:
                    score_away += 1
                zone = 'midfield'
                possession = 'home'

    w['home']['pred score'] = score_home
    w['away']['pred score'] = score_away
    
    logger.info('Pred Score Home: {} Away: {}'.format(score_home, score_away))

    return w


def simulation(data, t1, t2, c1, c2, c3, c4, c5, c6, f1, f2, f3):
    quality = 0
    win = 0
    total = 0

    teams = [t1, t2]

    w = {}
    for i,t in enumerate(['home', 'away']):
        w[t] = {}
        w[t]['g'] = worth_goalie(data[teams[i]]['goalie'])
        w[t]['d'] = worth_defense(data[teams[i]]['defense'],f1[teams[i]])
        w[t]['m'] = worth_midfield(data[teams[i]]['midfield'],f2[teams[i]])
        w[t]['a']  = worth_attack(data[teams[i]]['forward'],f3[teams[i]])
        w[t]['team'] = teams[i]
        w[t]['pred score'] = None
        
        logger.warning('{} {} {}'.format(w[t]['team'], 'Goalie', w[t]['g']))
        logger.warning('{} {} {}'.format(w[t]['team'], 'Defense', w[t]['d']))
        logger.warning('{} {} {}'.format(w[t]['team'], 'Midfield', w[t]['m']))
        logger.warning('{} {} {}'.format(w[t]['team'], 'Attack', w[t]['a']))

    sh = 0
    sa = 0
    rep = 1000
    for i in range(rep):
        w = predict(w, c1, c2, c3, c4, c5, c6)
        sh += w['home']['pred score']
        sa += w['away']['pred score']

    w['home']['pred score'] = round(sh / rep, 2)
    w['away']['pred score'] = round(sa / rep, 2)
    print('Pred.', w['home']['pred score'], w['away']['pred score'])



def main():

    with open('teams.json', 'r') as infile:
        data = json.load(infile)

    c1 = 0.06766951943225229
    c2 = 0.0033648527825174803
    c3 = 0.23140406859015059
    c4 = 0.4
    c5 = 0.3
    c6 = 0.3

    t1 = 'Sweden'
    t2 = 'Belgium'

    f1 = {}
    f2 = {}
    f3 = {}

    f1[t1] = 4
    f2[t1] = 4
    f3[t1] = 2
    f1[t2] = 4
    f2[t2] = 4
    f3[t2] = 2

    simulation(data, t1, t2, c1, c2, c3, c4, c5, c6, f1, f2, f3)


if __name__ == '__main__':
    main()
