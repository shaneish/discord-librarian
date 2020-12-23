from sportsreference.nfl.teams import Teams
import pandas as pd
from urllib.error import HTTPError

# read TheLibrarians Discord token
def load_token(token_file='./token'):
    with open(token_file, "r") as file:
        token = file.read()
        return token

def columnize(l, cols=3):
    tracker = dict()
    for ndx, s in enumerate(l):
        cur_s = tracker.get(ndx % cols, len(s))
        if len(s) > cur_s:
            tracker[ndx % cols] = len(s)
        else:
            tracker[ndx % cols] = cur_s
    return tracker

def cprint(string_list, cols=2, sep="  "):
    '''
    Function to print long lists more compactly.
    Uncomment the comments to have it print perfect columns in terminal.
    Unfortunately doesn't translate to Discord.

    ::string_list List[Str]:: list of strings
    ::cols Int:: number of columns to break up
    ::spaces Int:: number of spaces to add between words
    
    Returns: [Str]
    '''
    max_length = columnize(string_list, cols=cols)
    s = f"```{str(string_list[0]).ljust(max_length[0])}"
    for ndx, site in enumerate(string_list[1:]):
        column = (ndx + 1) % cols
        if column == 0:
            s += f"\n{site.ljust(max_length[0])}"
        else:
            s += f"{sep}{site.ljust(max_length[column])}"
    return s + "```"

def cprint_df(df):
    '''
    Similar to cprint above but takes a Pandas dataframe and returns a string to print the dataframe in Discord

    ::df pandas.DataFrame:: Pandas dataframe to print in Discord chat
    '''
    df_list = list(df.columns)
    num_cols = len(df_list)
    for row in df.to_numpy():
        df_list += list(row)
    df_no_nulls = list(map(str, map(remove_none_games, df_list)))
    return cprint(df_no_nulls, num_cols)

nfl_map = {"Tennessee Titans": "OTI","Kansas City Chiefs": "KAN","Green Bay Packers": "GNB","Seattle Seahawks": "SEA","Buffalo Bills": "BUF",
            "Baltimore Ravens": "RAV","Tampa Bay Buccaneers": "TAM","Indianapolis Colts": "CLT","New Orleans Saints": "NOR","Arizona Cardinals": "CRD",
            "Las Vegas Raiders": "RAI","Cleveland Browns": "CLE","Pittsburgh Steelers": "PIT","Minnesota Vikings": "MIN","Atlanta Falcons": "ATL",
            "Miami Dolphins": "MIA","Los Angeles Rams": "RAM","Dallas Cowboys": "DAL","Detroit Lions": "DET","San Francisco 49ers": "SFO",
            "Los Angeles Chargers": "SDG","Carolina Panthers": "CAR","Houston Texans": "HTX","Chicago Bears": "CHI","Philadelphia Eagles": "PHI",
            "Washington Football Team": "WAS","New England Patriots": "NWE","Denver Broncos": "DEN","Jacksonville Jaguars": "JAX","Cincinnati Bengals": 
            "CIN","New York Giants": "NYG","New York Jets": "NYJ"}

def team_code(team_name, name_map=nfl_map):
    '''
    Retrieves the proper lookup code for the team searched for

    ::team_name Str:: location or name of team
    ::name_map Dict:: Dictionary mapping to lookup codes
    '''
    for team in name_map:
        if team_name.lower() in team.lower():
            return name_map[team]

def team_search(team_code):
    teams = Teams()
    return teams(team_code)

return_team = lambda team_name, name_map=nfl_map: team_search(team_code(team_name, name_map))

# simple function to replace Nones in list with 'Future game'
remove_none_games = lambda s: s if s is not None else 'Future game'

def team_schedule(team_name, name_map=nfl_map):
    '''
    Returns formatted table showing a team's yearly schedule and wins/losses

    ::team_name Str:: Team to lookup
    ::name_map Dict:: Dictionary mapping to lookup codes
    '''
    try:
        schedule = team_search(team_code(team_name, name_map)).schedule.dataframe[['date', 'location', 'opponent_name', 'result']]
        schedule = schedule.rename(columns={'date': 'Date', 'location': 'Location', 'opponent_name': 'Opponent', 'result': 'Result'})
    except (AttributeError, HTTPError) as error:
        return "**Not a valid team**"
    return cprint_df(schedule)

def gen_leaderboard(name_map=nfl_map, teams=[]):
    team_finder = Teams()
    if len(teams) > 0:
        try:
            teams = [team_finder(team_code(team, name_map)) for team in teams]
        except (AttributeError, HTTPError) as error:
            return "**Contains an incorrect team name dummy."
    else:
        teams = team_finder
    teams = [team.dataframe[['name', 'rank', 'wins', 'losses', 'win_percentage', 'games_played']] for team in teams]
    leaderboard = pd.concat(teams).rename(columns={'name': 'Team', 'rank': 'Rank', 'wins': 'Wins', 'losses': 'Losses', 'win_percentage': 'Win Pct', 'games_played': 'Games'})
    return leaderboard

def split_df(df, row_limit=15):
    if df.shape[0] > row_limit:
        return [df[:row_limit]] + split_df(df[row_limit:])
    else:
        return [df]