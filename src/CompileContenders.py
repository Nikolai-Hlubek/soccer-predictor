import json

players = {}
with open('EM2016-PlayersNetWorth.csv', 'r') as infile:
    line = infile.readline()  # header
    line = infile.readline()
    while line != '':
        l = line[:-1].split(',')
        players[l[0]] = float(l[1])
        line = infile.readline()

teams = {}
with open('EM2016-Teams.csv', 'r') as infile:
    for i in range(24):
        line1 = infile.readline()
        line2 = infile.readline()
        line3 = infile.readline()
        line4 = infile.readline()
        line5 = infile.readline()
        line6 = infile.readline()
        line7 = infile.readline()
        line8 = infile.readline()
        
        team = line1[:-1]
        fifa_ranking = float(line2.split(' ')[2][:-1])
        formations = line3.split(' ')[1:]
        goalie = line4[13:-1].split(', ')
        defense = line5[11:-1].split(', ')
        midfield = line6[13:-1].split(', ')
        forward = line7[10:-1].split(', ')
       
        goalie_d = {}
        for g in goalie:
            goalie_d[g] = players[g]
        defense_d = {}
        for d in defense:
            defense_d[d] = players[d]
        midfield_d = {}
        for m in midfield:
            midfield_d[m] = players[m]
        forward_d = {}
        for f in forward:
            forward_d[f] = players[f]



        teams[team] = { 
                'fifa_ranking' : fifa_ranking,
                'formations' : formations,
                'goalie' : goalie_d,
                'defense' : defense_d,
                'midfield' : midfield_d,
                'forward' : forward_d,
        }

with open('teams.json', 'w') as outfile:
    json.dump(teams, outfile)

