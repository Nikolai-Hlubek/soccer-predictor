import json
import logging
import random
import math

logging.basicConfig(level=logging.WARNING)

#logging.getLogger(__name__).setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
#logger.setLevel(logging.WARNING)


def worth_goalie(p):
    worth = 0.0
    for pi in p:
        if 'worth' not in pi:
            continue
        if pi['pos'] in ['GK', 'Goalkeeper']:
            if pi['worth'] != None:
                worth = pi['worth']
            else:
                worth = 0.1
    return worth


def worth_defense(p):
    worth = 0.0
    for pi in p:
        if 'worth' not in pi:
            continue
        if pi['pos'] in ['CB', 'LB', 'RB']:
            if pi['worth'] != None:
                worth += pi['worth']
    return worth


def worth_midfield(p):
    worth = 0.0
    for pi in p:
        if 'worth' not in pi:
            continue
        if pi['pos'] in ['RM', 'LM', 'CM', 'AM', 'LW', 'RW', 'DM']:
            if pi['worth'] != None:
                worth += pi['worth']
    return worth


def worth_attack(p):
    worth = 0.0
    for pi in p:
        if 'worth' not in pi:
            continue
        if pi['pos'] in ['RF', 'LF', 'CF']:
            if pi['worth'] != None:
                worth += pi['worth']
    return worth


def worth_team(p):
    worth = 0
    for pi in p:
        if 'worth' not in pi:
            continue
        if pi['worth'] != None:
            worth += pi['worth']
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
    logger.info('Real Score Home: {} Away: {}'.format(w['home']['real score'], w['away']['real score']))

    return w


def train_model(data, c1, c2, c3, c4, c5, c6):
    quality = 0
    win = 0
    total = 0

    for ctr,d in enumerate(data):
        if ctr == 60:
            break

        w = {}
        for t in ['home', 'away']:
            w[t] = {}
            w[t]['g'] = worth_goalie(d[t]['start'])
            w[t]['d'] = worth_defense(d[t]['start'])
            w[t]['m'] = worth_midfield(d[t]['start'])
            w[t]['a']  = worth_attack(d[t]['start'])
            w[t]['name'] = d[t]['team']
            w[t]['real score'] = d[t]['score']
            w[t]['pred score'] = None
            
            s = 0
            if w[t]['g'] != None:
                s += w[t]['g']
            if w[t]['d'] != None:
                s += w[t]['d']
            if w[t]['m'] != None:
                s += w[t]['m']
            if w[t]['a'] != None:
                s += w[t]['a']
            logger.debug(d[t]['start'])
            if s < worth_team(d[t]['start']) - 0.001:
                logger.warning('Not all positions used for {}'.format(d[t]['team']))
                logger.info(s)
                logger.info(worth_team(d[t]['start']))
            else:
                logger.warning('{} {} {}'.format(d[t]['team'], 'Goalie', w[t]['g']))
                logger.warning('{} {} {}'.format(d[t]['team'], 'Defense', w[t]['d']))
                logger.warning('{} {} {}'.format(d[t]['team'], 'Midfield', w[t]['m']))
                logger.warning('{} {} {}'.format(d[t]['team'], 'Attack', w[t]['a']))

        sh = 0
        sa = 0
        rep = 100
        for i in range(rep):
            w = predict(w, c1, c2, c3, c4, c5, c6)
            sh += w['home']['pred score']
            sa += w['away']['pred score']

        w['home']['pred score'] = round(sh / rep, 2)
        w['away']['pred score'] = round(sa / rep, 2)
#        print('{} vs {}'.format(d['home']['team'], d['away']['team']))
#        print('Pred.', w['home']['pred score'], w['away']['pred score'])
#        print('Real.', w['home']['real score'], w['away']['real score'])

        quality += abs(w['home']['pred score'] - w['home']['real score']) + \
                abs(w['away']['pred score'] - w['away']['real score'])
        total += 1
        if (w['home']['real score'] > w['away']['real score']) \
                and (w['home']['pred score'] > w['away']['pred score']):
            win += 1
        if (w['home']['real score'] < w['away']['real score']) \
                and (w['home']['pred score'] < w['away']['pred score']):
            win += 1
        if (w['home']['real score'] == w['away']['real score']) \
                and (w['home']['pred score'] == w['away']['pred score']):
            win += 1


    return quality, win/total
        


def main():

    with open('qualifier_2.json', 'r') as infile:
        data = json.load(infile)

    c1 = 0.008
    c2 = 0.01
    c3 = 0.2
    c4 = 0.4
    c5 = 0.3
    c6 = 0.3

    last_fit = 1e99
    base_fit = 1e99

    while 1:
        c1 = random.uniform(0.0,0.1)
        c2 = random.uniform(0.0,0.1)
        c3 = random.uniform(0.0,0.4)
#        c4 = random.uniform(0.0,1.0)
#        c5 = random.uniform(0.0,1.0)
#        c6 = random.uniform(0.0,1.0)

        (last_fit, last_win) = train_model(data, c1, c2, c3, c4, c5, c6)
        
        if last_fit < base_fit:
            c1s = c1
            c2s = c2
            c3s = c3
            c4s = c4
            c5s = c5
            c6s = c6
            base_fit = last_fit
            print(last_fit, last_win, c1s, c2s, c3s, c4s, c5s, c6s)


if __name__ == '__main__':
    main()
