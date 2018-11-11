## About Iris (u/ChoicesBOT)

Iris (u/ChoicesBOT) is a simple Reddit reference bot for [r/Choices](https://www.reddit.com/r/Choices/) (a community for [Pixelberry's *Choices* mobile game](http://www.pixelberrystudios.com/)) that fetches information from the unofficial [Choices Wikia](http://choices-stories-you-play.wikia.com/wiki/Choices:_Stories_You_Play_Wikia) and returns it as a comment to the requester's comment. The bot's namesake is the AI [IRIS from the book *Endless Summer*](http://choices-stories-you-play.wikia.com/wiki/IRIS).

#### Reference Syntax

Iris responds to the "inline code" syntax on r/Choices - that is, it will look up words with grave accents (\`) on either side. Thus, `Maria` would conduct a search for "Maria". Iris can also search for multiple words/terms in the same comment and will return the results in a single comment. 

This behavior is derived from r/translator's [Ziwen](https://github.com/kungming2/translator-BOT).

#### Response 

Iris will reply with a comment containing the character's name, an image of them, a short description, and if available, a random trivia fact about them. Iris also includes a link to the Wikia page for that character and Tumblr/Twitter links featuring posts that have tagged that character.

The trivia fact is randomly selected from the character's page, and is wrapped in Reddit's spoiler Markdown syntax (`>!spoiler!<`) to prevent the comment from spoiling other readers.

##### Example Response Text

The following is an example of Iris's response to a reference request for the character [Quinn](http://choices-stories-you-play.wikia.com/wiki/Quinn_Kelly):

---

**[Quinn Kelly](http://choices-stories-you-play.wikia.com/wiki/Quinn_Kelly) | [Image](https://vignette.wikia.nocookie.net/choices-stories-you-play/images/a/a5/Quinn.jpg)**

Quinn, a character in the "Endless Summer" series, is one of the college students who won a contest to spend a week at La Huerta. She is one of Your Character's love interests. She is first seen in Book 1, Chapter 1.

*Did You Know?* ~~She is skilled at figure skating, but it's only a hobby for her.~~

Links: [Wikia](http://choices-stories-you-play.wikia.com/wiki/Quinn_Kelly) | [Tumblr](https://www.tumblr.com/search/quinn%20%23playchoices) | [Twitter](https://twitter.com/search?f=tweets&q=%40playchoices%20quinn)