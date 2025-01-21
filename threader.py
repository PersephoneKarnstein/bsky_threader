import nltk, collections, re, os
import numpy as np
from dotenv import load_dotenv
from atproto import Client, models

load_dotenv()

username = os.getenv("BSKY_USERNAME")
password = os.getenv("BSKY_PASSWORD")


paragraph = """
THIS IS A TEST OF A PROGRAM I'M WRITING, IGNORE THIS THREAD. TEXT IS FROM https://taliabhattwrites.substack.com/p/the-third-sex

Consider a mechanism whose sole function is to classify all inputs it receives as one of two categories: One and Zero. The inputs, it must be said, vary greatly in temperament, expression, embodiment, internality, and so on, but that isn’t as much of a hurdle for the machine as it seems. It has been programmed with a few simple lines of code that enable it to differentiate between Ones and Zeroes within acceptable margins of tolerance. Ones tend to look and behave like this, Zeroes tend to be like that. These truisms are crude, simplistic, and even reductive, true, but they work. As such, the machine chugs on, happily reducing complex inputs to a blunt binary classification, its delivery-day code having been deemed “good enough”.

Of course, there is still the matter of how the machine should behave when its schema fails, when it is presented with inputs that do indeed prove to be too ambiguous to easily classify. For however high the correlation between traits, sometimes a specimen that simply defies easy categorization will confound its decision-making, often enough to pose a problem. Does the code need to be updated? Almost certainly, but legacy code is a stubborn thing, mired in dependencies and versioning faff, deeply resistant to the most perfunctory of edits. Too many now rely on this iteration of the machine, on this particular instantiation of its logic, and it is almost universally agreed that any changes are best handled downstream—at least, among those with the power to change it.

The machine and its users are thus forced to consider: In the case of an “error”, a “mistake”, so to speak, is it better to classify something as a One or a Zero?
"""

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
        skeets[i+1]="..."+skeets[i+1]
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
