# read TheLibrarians Discord token
def load_token(token_file='./token'):
    with open(token_file, "r") as file:
        token = file.read()
        return token

# parse messages for saving to CSV
def parse_message(message):
    message_list = message.split("\n")
    return "\\n".join(message_list)