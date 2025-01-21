import nltk, collections, re, os, argparse
import numpy as np
from dotenv import load_dotenv
from rich_argparse import RichHelpFormatter
from atproto import Client, models

load_dotenv()

username = os.getenv("BSKY_USERNAME")
password = os.getenv("BSKY_PASSWORD") #get your bsky creds from an env file

parser = argparse.ArgumentParser(
                    prog='python threader.py',
                    description='Bluesky Thread Poster: convert long chunks of text into threaded bluesky posts', formatter_class=RichHelpFormatter)

parser.add_argument('filename') # positional argument
args = parser.parse_args()

with open(args.filename, "r") as f:
    paragraph = f.read()

nltk.download('punkt')
sentences = nltk.sent_tokenize(paragraph) #break into sentences with NLP

#we're gonna want to break overlong sentences on a space
def find_closest_character(string, char, index):
    """Finds the closest occurrence of 'char' to the given 'index' in 'string'."""

    left_index = string.rfind(char, 0, index)
    right_index = string.find(char, index)

    if left_index == -1:
        return right_index
    elif right_index == -1:
        return left_index
    else:
        return left_index if index - left_index < right_index - index else right_index

#can run repeatedly for sentences > 600 characters long
while True:
    new_sentence_list = []
    for sentence in sentences:
        if len(sentence)<200: 
            new_sentence_list.append(sentence)
        else:
            closest_index = find_closest_character(sentence, " ", int(len(sentence)/2))
            new_sentence_list.append(sentence[:closest_index])
            new_sentence_list.append(sentence[closest_index+1:])
    
    if collections.Counter(sentences) == collections.Counter(new_sentence_list): #stop when you don't need to split it anymore
        sentences = new_sentence_list
        break
    else: 
        sentences = new_sentence_list
        continue

#initialize our skeets list as including the first sentence
skeets = [sentences.pop(0)]

# Break by sentence into chunks that will fit the character limit
for i in np.arange(len(sentences)):
    next_sentence = sentences.pop(0) 

    if len(skeets[-1])+len(next_sentence) < 287: #bsky allows 300 characters but we alot 10 chars of space for the thread counter and 3 for an ellipsis
        skeets[-1]+=" " + next_sentence
    else: 
        skeets.append(next_sentence)

# add the thread counter
for i, skeet in enumerate(skeets):
    if not re.match(r"\.|!|\?|(...)|\"", skeets[i].strip()[-1]): #if the skeet doesn't look like the end of a sentence; add ellipses
        skeets[i]+="..."
        try:
            skeets[i+1]="..."+skeets[i+1]
        except IndexError: pass #catches the case where it ends in something other than a full sentence
    else: 
        pass
    
    skeets[i] += f" 🧵 ({i+1}/{len(skeets)})"
    print(skeets[i], "\n\n")
    

#log into bluesky
client = Client()
client.login(username, password)

#post anchor post
original_post = client.send_post(skeets.pop(0))
root = models.create_strong_ref(original_post)
parent = models.create_strong_ref(original_post)

#reply with next post in thread
for i in np.arange(len(skeets)):
    next_skeet = skeets.pop(0) 
    skeeted = client.send_post(
        text=next_skeet,
        reply_to=models.AppBskyFeedPost.ReplyRef(parent=parent, root=root)
    )
    parent = models.create_strong_ref(skeeted)
