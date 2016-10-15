list <- structure(NA,class="result")
"[<-.result" <- function(x,...,value) {
  args <- as.list(match.call())
  args <- args[-c(1:2,length(args))]
  length(value) <- length(args)
  for(i in seq(along=args)) {
    a <- args[[i]]
    if(!missing(a)) eval.parent(substitute(a <- v,list(a=a,v=value[[i]])))
  }
  x
}

read_players <- function(){
  players <- read.csv('EM2016-PlayersNetWorth.csv')
  colnames(players) <- c('Name', 'Worth')
  players
}

read_teams <- function(players){
  teams <- data.frame()
  
  f <- file('EM2016-Teams.csv', 'r')
  for( i in 1:24 ){
    block <- readLines(f,n=8)
    country <- block[[1]]
    rank <- strsplit(block[[2]], split=': ')[[1]]
    formation <- strsplit(block[[3]], split=': ')[[1]]
    goal <- strsplit(block[[4]], split=': ')[[1]]
    defence <- strsplit(block[[5]], split=': ')[[1]]
    midfield <- strsplit(block[[6]], split=': ')[[1]]
    forward <- strsplit(block[[7]], split=': ')[[1]]
    
    goalies <- strsplit(goal[[2]], split=', ')
    for ( g in goalies[[1]] ){
      n <- which(players['Name'] == g)
      if( length(n)>0 ){
        players[n, 'Position'] <- goal[[1]]
        players[n, 'Country'] <- country
      }
    }
    defenders <- strsplit(defence[[2]], split=', ')
    for ( d in defenders[[1]] ){
      n <- which(players['Name'] == d)
      if( length(n)>0 ){
        players[n, 'Position'] <- defence[[1]]
        players[n, 'Country'] <- country
      }
    }
    midfielders <- strsplit(midfield[[2]], split=', ')
    for ( m in midfielders[[1]] ){
      n <- which(players['Name'] == m)
      if( length(n)>0 ){
        players[n, 'Position'] <- midfield[[1]]
        players[n, 'Country'] <- country
      }
    }
    forwarders <- strsplit(forward[[2]], split=', ')
    for ( fw in forwarders[[1]] ){
      n <- which(players['Name'] == fw)
      if( length(n)>0 ){
        players[n, 'Position'] <- forward[[1]]
        players[n, 'Country'] <- country
      }
    }
    
    teams[country, rank[[1]]] <- as.numeric(rank[[2]])
    print(formation[[2]])
    teams[country, formation[[1]]] <- formation[[2]]
  }
  close(f)
  list(players, teams)
}

country_worth <- function(players, teams){
  for( country in rownames(teams) ){
    pc <- subset(players, subset=(players$Country == country))
    teams[country, 'Worth'] <- sum(pc$Worth)
  }
  teams
}

formation_worth <- function(pc, formation){
  worth <- list()

  x <- subset(pc, subset=(pc$Position == 'Goalkeepers'))
  worth['Goalie'] <- max(x$Worth)
  players <- 1
    
  x <- subset(pc, subset=(pc$Position == 'Defenders'))
  n <- substring(formation, 1, 1)
  n <- as.numeric(n)
  worth['Defense'] <- sum(sort(x$Worth, decreasing=TRUE)[1:n])
  players <- players + n
    
  x <- subset(pc, subset=(pc$Position == 'Midfielders'))
  n <- strsplit(formation, '-')[[1]]
  n <- n[c(-1, -length(n))]
  n <- lapply(n, as.numeric)
  n <- sum(unlist(n))
  worth['Midfield'] <- sum(sort(x$Worth, decreasing=TRUE)[1:n])
  players <- players + n

  x <- subset(pc, subset=(pc$Position == 'Forwards'))
  n <- substring(formation[[1]], nchar(formation), nchar(formation))
  n <- as.numeric(n)
  worth['Attack'] <- sum(sort(x$Worth, decreasing=TRUE)[1:n])
  players <- players + n

  print(players)
  worth
}

players <- read_players()
list[players, teams] <- read_teams(players)
teams <- country_worth(players, teams)

country <- 'Portugal'
country_players <- subset(players, subset=(players$Country == country))
country_formations <- teams[country, 'Formation']
country_formations <- strsplit(country_formations, split=', ')[[1]]
res <- formation_worth(country_players, country_formations[[1]])
