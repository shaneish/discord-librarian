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
    with open(paywall_file, 'r') as file:
        paywalled_sites = file.read().split("\n")
        return [i for i in paywalled_sites if i != ""]

# read TheLibrarians Discord token
def load_token(token_file='token'):
    with open(token_file, "r") as file:
        token = file.read()
        return token

def load_malarkey(malarkey_file='malarky.pkl'):
    if path.exists(malarkey_file):
        with open(malarkey_file, 'rb') as file:
            return pickle.load(file)
    else:
        return MalarkeyDict()

def save_malarkey(malarkey_dict, malarkey_file='malarky.pkl'):
    with open(malarkey_file, 'wb') as file:
        pickle.dump(malarkey_dict, file)

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

class MalarkeyDict:

    def __init__(self):
        self._keys = list()
        self._value_dict = dict()

    def _get_index(self, keys):
        keys = self._smooth_input(keys)
        for key in self._keys:
            if keys.issubset(key):
                return self._keys.index(key)
        return None

    def _compatible_key(self, keys):
        keys = self._smooth_input(keys)
        compat_test = [bool(keys.intersection(key)) for key in self._keys]
        if sum(compat_test) < 1:
            return len(self._keys)
        elif sum(compat_test) == 1:
            return compat_test.index(True)

    def _update_key(self, new_key):
        new_key = self._smooth_input(new_key)
        test_list = [bool(new_key.intersection(key)) for key in self._keys]
        if sum(test_list) == 1:
            index = test_list.index(True)
            self._keys = self._keys[:index] + [self._keys[index].union(new_key)] + self._keys[index+1:]
        elif sum(test_list) < 1:
            self._keys.append(new_key)

    def add_to_group(self, new_key):
        new_key = self._smooth_input(new_key)
        test_list = [bool(new_key.intersection(key)) for key in self._keys]
        if sum(test_list) == 1:
            index = test_list.index(True)
            self._keys = self._keys[:index] + [self._keys[index].union(new_key)] + self._keys[index+1:]
        else:
            raise ValueError("Cannot add to conflicting groups.")
    
    '''
    def remove_from_group(self, single_key):
        new_key = {single_key}
        test_list = [bool(new_key.intersection(key)) for key in self._keys]
        if sum(test_list) == 1:
            index = test_list.index(True)
            self._keys = self._keys[:index] + [self._keys[index].remove(single_key)] + self._keys[index+1:]
        else:
            raise ValueError("Not found in current groups.")
    '''

    def __len__(self):
        return len(self._keys)
    
    def _smooth_input(self, key_input):
        if type(key_input) == str:
            return {key_input.lower()}
        else:
            return {str(key).lower() for key in key_input}

    def __setitem__(self, keys, value):
        keys = self._smooth_input(keys)
        value = float(value)
        compat_index = self._compatible_key(keys)
        if compat_index is not None:
            self._update_key(keys)
            self._value_dict[compat_index] = value
        else:
            raise ValueError("New key is incompatible with old.")

    def __getitem__(self, key):
        key = str(key)
        index = self._get_index(key)
        if index is None:
            return 0
        else:
            return self._value_dict[index]
    
    def __str__(self):
        return "{" + "\n".join([f"{key}: {self._value_dict[self._get_index(key)]}" for key in self._keys]) + "}"
    
    def __repr__(self):
        return self.__str__()

    def measure_malarkey(self, sentence):
        words = [strip_word(word) for word in sentence.replace("\n", "").replace("\t", "").replace("-", " ").replace("_", " ").split(" ")]
        groups_used = list()
        malarkey_count = 0
        for word in words:
            if self._get_index(word) not in groups_used:
                malarkey_count += self.__getitem__(word)
                groups_used.append(self._get_index(word))
        return malarkey_count