#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Iris is a simple reference bot for r/Choices to look up characters and other information from the Choices Wikia at:
http://choices-stories-you-play.wikia.com.

This is based off of the module at https://github.com/Timidger/Wikia, with a few calls to directly access the Wikia API.

Here are some WikiaPage object attributes to note:

* `original_title`, the title of this page, as the Wikia defines it.
* `summary`, the initial text of this page.
* `url`, the URL at which this page is located.
* `pageid`, the master ID of the page. Needed for exact matches.
* `images`, list of images on the page.
* `related_pages`, pages which are related to the current one.
* `sections`, which feeds into the mothod `section` to get the particular one.
"""

import praw
import wikia
import json
import requests
import google

import random
import re
import os
import time
import traceback


"""INTIALIZATION"""

VERSION_NUMBER = "0.6.8 Beta"
SUBREDDIT = 'Choices+testingground4bots'
WAIT = 15  # Number of seconds to pause before restarting. Iris runs continuously and not on a loop.
SOURCE_FOLDER = os.path.dirname(os.path.realpath(__file__))  # Fetch the absolute directory the script is in.
FILE_ADDRESS_CREDENTIALS = SOURCE_FOLDER + "/_credentials.json"

"""LOAD CREDENTIALS"""


def load_credentials():
    """
    Function that takes information about login and OAuth access from an external JSON file and loads it as a
    dictionary.

    :return: A dictionary with keys for important variables needed to log in and authenticate.
    """

    # Load the JSON file.
    f = open(FILE_ADDRESS_CREDENTIALS, 'r', encoding='utf-8')
    credentials_data = f.read()
    f.close()

    # Convert the JSON data into a Python dictionary.
    credentials_data = json.loads(credentials_data)

    return credentials_data


choicesbot_info = load_credentials()
USERNAME = choicesbot_info['username']
PASSWORD = choicesbot_info['password']
APP_ID = choicesbot_info['app_id']
APP_SECRET = choicesbot_info['app_secret']

"""TEMPLATES"""

USER_AGENT = 'Iris v{} (u/{}), a Wikia reference helper written by u/kungming2.'.format(VERSION_NUMBER, USERNAME)
BOT_DISCLAIMER = ("\n\n---\n^Iris: ^a ^reference ^bot ^for ^r/Choices ^| "
                  "[^Bot ^Info/Support](https://www.reddit.com/message/compose/?to=kungming2&subject=About+Iris)")
ENTRY_TEMPLATE = '''
### [{character_name}]({wikia_link}) | {character_image}

{character_summary}

{trivia_bit}

Links: [Wikia]({wikia_link}) | [Tumblr]({tumblr_link}) | [Twitter]({twitter_link})
'''


def get_wiki_page_google(search_term):  # A function that uses Google to look for the most appropriate Wikia page. 

    google_urls = []
    
    for url in google.search(search_term + ' choices-stories-you-play.wikia.com', num=2, stop=2):
        google_urls.append(url)
        
    url_to_access = google_urls[0]
    derived_title = url_to_access.split('wiki/', 1)[1].replace("_", " ")
    # wikia_object = wikia.page(sub_wikia='choices-stories-you-play', title=derived_title)
    
    return derived_title


def get_wiki_page(search_term):  # Get the Wikia page for a particular search term. In this case, it gets the best 1.
    
    try:
        list_of_results = wikia.search(sub_wikia='choices-stories-you-play', query=search_term, results=5)
    except ValueError:  # This search for this term failed.
        return None

    best_result = list_of_results[0]
    if " " not in best_result:  # This is a single title article, which causes problems. 
        best_result = get_wiki_page_google(search_term)
    
    # Return it as an WikiaPage object.
    best_result_object = wikia.page(sub_wikia='choices-stories-you-play', title=best_result)
    
    return best_result_object


def get_random_character_trivia(page_id):  # Get a random trivia about a character.

    trivia_data_list = None
    all_trivia_data = []  # A list of all the trivia pieces for a character.

    # Access the Wikia API and get the page's sections.
    query_link = 'http://choices-stories-you-play.wikia.com/api/v1/Articles/AsSimpleJson?id={}'.format(page_id)
    retrieved_data = requests.get(query_link)
    data_list = retrieved_data.json()['sections']
    
    # Look for the page's "Trivia" section. 
    for section_dict in data_list:
        if section_dict['title'].lower() == "trivia":
            if 'elements' in section_dict['content'][0]:
                trivia_data_list = section_dict['content'][0]['elements']
    
    # Exit if we found no trivia data.
    if trivia_data_list is None:
        return None
    
    # Compile all the trivia sentences into a list.
    for tidbit_dict in trivia_data_list:
        tidbit = tidbit_dict['text'].strip()
        all_trivia_data.append(tidbit)
    
    # Pick a random factoid.
    random_trivia = random.choice(all_trivia_data)
    
    return random_trivia


def get_short_summary(page_id):  # Get literally only the first sentence about a character.
    
    summary_text = None
    
    # Access the Wikia API and get the page's sections.
    query_link = 'http://choices-stories-you-play.wikia.com/api/v1/Articles/AsSimpleJson?id={}'.format(page_id)
    retrieved_data = requests.get(query_link)
    data_list = retrieved_data.json()['sections']

    # Look for the page's "Trivia" section. 
    for section_dict in data_list:
        if section_dict['level'] == 1:
            if 'text' in section_dict['content'][0]:
                summary_text = section_dict['content'][0]['text'].strip()
    
    return summary_text  
    

def form_character_comment(character_name):  # Make a nice Markdown comment from a character name passed to it.

    # Get the WikiaPage Object.
    our_object = get_wiki_page(character_name)
    
    if our_object is None:
        return None
    
    name = our_object.original_title
    try:
        headshot = our_object.images[0]
        headshot = "[Image]({})".format(headshot)
    except KeyError:  # There is no image found.
        headshot = ""

    wikia_url = our_object.url.replace(" ", "_")
    page_id = our_object.pageid
    
    # Get the summary. Then add spoiler tags to it.
    summary = get_short_summary(page_id)
    # summary = ">!{}<!".format(summary)
    
    # We don't want pages with these in the title.
    excluded_keywords = ['Theory', 'Theories', 'Choices', 'Book', "Your "]
    for keyword in excluded_keywords:
        if keyword in name:  # This matches.
            return None  # Exit.
    
    # Get trivia.
    trivia = get_random_character_trivia(page_id)
    if trivia is not None:
        trivia = '*Did You Know?* >!{}!<'.format(trivia)
    else: 
        trivia = ''
    
    # Form the Tumblr link.
    tumblr_url = "https://www.tumblr.com/tagged/{}+%23playchoices".format(name.lower().replace(" ", "-"))

    # Form the Twitter link.
    twitter_url = "https://twitter.com/search?f=tweets&q=%40playchoices%20{}"
    if " " in name:
        twitter_url = twitter_url.format(name.split(' ', 1)[0])  # Twitter search for just the first name.
    else:
        twitter_url = twitter_url.format(name)

    new_comment = ENTRY_TEMPLATE.format(character_name=name, character_image=headshot, character_summary=summary,
                                        trivia_bit=trivia, wikia_link=wikia_url, tumblr_link=tumblr_url,
                                        twitter_link=twitter_url)

    return new_comment


def parse_comment_search_terms(comment_text):
    """
    This function checks a comment for text between grave accents. `
    It then gets them as a list and then collates the returned information into one whole piece. 
    
    """
    formatted_entries = []
    headers = []

    comment_text = comment_text.replace('\`', '`')  # The redesign sometimes introduces slashes.

    # Get everything between the graves.
    matches = re.findall('`(.*?)`', comment_text, re.DOTALL)
    
    if len(matches) == 0:
        return None  # We exit if we cannot find anything.

    matches = [x.strip() for x in matches] 
    for match in matches:
        character_comment = form_character_comment(match.title())
        if character_comment is not None:
            formatted_entries.append(character_comment)
    
    # Pull it all together.
    if len(formatted_entries) == 0:
        return None  # No entries, exit.
    else:
        # We dedupe the entries here and make sure we don't have two entries for the same character.
        for entry in formatted_entries:
            first_line = entry.split('\n\n', 1)[0].strip()  # Get just the character heading.
            if first_line not in headers:
                headers.append(first_line)
            else:  # The header is already recorded. We don't need this section again.
                formatted_entries.remove(entry)  # Remove the entry from the list.

        # Pull everything together
        body = '\n\n'.join(formatted_entries)

        return body


'''MAIN RUNTIMES'''


def main_login():
    """
    A simple function to log in to Reddit.

    :return: Nothing, but a global `reddit` variable is declared.
    """

    global reddit  # Declare the connection as a global variable.

    # Authenticate the connection.
    reddit = praw.Reddit(client_id=APP_ID, client_secret=APP_SECRET, password=PASSWORD,
                         user_agent=USER_AGENT, username=USERNAME)
    print("[Iris] v{} Startup: Logging in as u/{}.".format(VERSION_NUMBER, USERNAME))

    return


def main_stream():
    """
    The main function to fetch comments from the subreddit. 
    
    """

    r = reddit.subreddit(SUBREDDIT)

    for comment in r.stream.comments():  # Watching the stream...
    
        comment_text = comment.body
        
        grave_count = comment_text.count('`')
        if grave_count < 2:  # Doesn't have our keyword.
            continue
        
        try:
            comment_author = comment.author.name
        except AttributeError:
            # Author is deleted. We don't care about this post.
            continue

        if comment_author == USERNAME:
            # Don't reply to yourself, bot!
            continue
        
        if comment.saved:  # Saved comments have already been acted on.
            continue
        
        # Finally, we can act. 
        comment.save()  # Save this so we won't reply to it more than once.
        comment_permalink = comment.permalink
        reply_data = parse_comment_search_terms(comment_text)
        
        # If we have nothing found, continue.
        if reply_data is None:
            continue
        else:
            reply_body = reply_data + BOT_DISCLAIMER
            comment.reply(reply_body)
            print("Replied to u/{} with lookup data. Link at: {}".format(comment_author, comment_permalink))
        
    return
            

'''RUNNING THE BOT'''

# This is the actual loop that runs the top-level MAIN functions of the bot.

# Log in and authenticate with Reddit.
main_login()

'''
while True:
    word = input("Enter the input text: ")
    if word == 'x':
        break
    returned_info = parse_comment_search_terms(word)
    print(returned_info)
'''


while True:
    # noinspection PyBroadException
    try:
        main_stream()
    except Exception as e:
        traceback.print_exc()

    print('Iris will restart in {} seconds. \n'.format(WAIT))
    time.sleep(WAIT)
