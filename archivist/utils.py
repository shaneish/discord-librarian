from urllib.parse import urlparse
import pickle
from os import path


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

    ::string_list [List[Str]]:: list of strings
    ::cols [Int]:: number of columns to break up
    ::spaces [Int]:: number of spaces to add between words
    
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


def url_validator(x):
    '''
    Quick function to validate if 'x' is a proper URL or not

    Returns: Boolean
    '''
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False


# read the paywalled config file to read all websites currently redirected by TheLibrarian
def load_paywalls(paywall_file='paywalled'):
    if path.exist(paywall_file):
        file_to_read = paywall_file
    else:
        file_to_read = "base_paywalls"
    with open(file_to_read, 'r') as file:
        paywalled_sites = file.read().split("\n")
        return [i for i in paywalled_sites if i != ""]


# read TheLibrarians Discord token
def load_token(token_file='token'):
    with open(token_file, "r") as file:
        token = file.read()
        return token


# quick way to identify 'and' word combinations
def and_includes(message, *words):
    return all([(word.lower() in message.lower()) for word in words])


# quick way to identify 'or' word combinations
def or_includes(message, *words):
    return max([(word.lower() in message.lower()) for word in words])


# strip punctuation from a string
def strip(s):
    return "".join([char for char in s if char not in '~`!@#$%^&*()-_+=[]{};:"\'<>,./?'])


def strip_word(word):
    new_word = list()
    for letter in word:
        if letter not in "!@#$%^&*()=+[]}{|;:'\",<.>/?":
            new_word.append(letter)
    return "".join(new_word)