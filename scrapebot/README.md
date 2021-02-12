# ScrapeBot

ScrapeBot examines public web sites for relevant press releases and emails the title and link to each PR that meets the matching criteria.

## Prerequisites

You only need to complete these steps once:

1. Check that you have Python 3.8 (or greater) on your computer

Go to a command prompt or terminal, enter `python -V` (with a capital V) the. You should see output like: `Python 3.8.6` If you don't get that output or you have an older version, go here to download and install Python: https://www.python.org/downloads/

2. Check that `git` is installed

From a command prompt or terminal, enter `git --version`. You should see output like: `git version 2.24.0` If you don't try `pip3 -V`

3. Create a Python virtual environment for this project:

```bash
python -m venv ~/.venv/scrapebot
```

## Cloning this repository onto your computer

From a command prompt, change to any directory where you'd like to store the files for the repositor. After that clone, the repository using this command:

```bash
git clone https://github.com/Lakdawala-Lab/PHIGHT_COVID_Sources.git`
```

If you've already set up ssh keys for use with git you can instead use:

```bash
git clone git@github.com:Lakdawala-Lab/PHIGHT_COVID_Sources.git
```

## Installation

To activate the virtual environment you created above:

```bash
source ~/.venv/scrapebot/bin/activate
```

To install the Python modules used by this project, change to the `scrapebot` directory in the repository, then:

```bash
pip install -r requirements.txt
```

## Running the bot

Be sure the virtual environment is active:

```bash
source ~/.venv/scrapebot/bin/activate
```

To run the bot, with a "Minimum Date" of January 1, 2021:

```bash
python -m flow run 2021-01-01
```

This will run the bot on your local machine and will log output
that you can examine.

## Understanding the code

The bot uses an open source library called Prefect to create 
a simple workflow. The basic building blocks of Prefect are tasks
and flows. Tasks are individual pieces of work to be done and flows
are collections of tasks. Tasks can depend on other tasks and can
pass results to other tasks. You can learn more about 
[Prefect here](https://prefect.io). The code for the tasks and flow
are in `flow.py`

To interact with web pages, the bot uses an open source library
called BeautifulSoup. It allows the bot to request a particular 
web page and then examine the contents of the page. The code for
the web interaction is in `web.py`

## Flow parameters and configuration

You can configure the flow by passing a variety of parameters or just using default parameters:

* min_date: the bot will only examine press releases on or after this date
* states_to_run: the list of 2-character state abbreviation codes to check
* relevant_title_phrases: words or phrases to check for in the press release titles
* email_list: list of email addresses to send to
* really_send_email: true or false for whether to send email
* state_config: configuration settings for all states

The default values for the above parameters are:

```python
min_date = Parameter("min_date", default="2020-11-01", required=True)
state_config = Parameter(
    "state_config",
    default={
        "MT": {
            "url": "https://news.mt.gov/Home/rss/category/24469/governors-office",
            "type": "RSS",
            "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss z",
            "contentTag": "content:encoded",
            "class": "sources.MTGovNews",
        },
        "ND": {
            "url": "https://www.governor.nd.gov/rss/news",
            "type": "RSS",
            "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss ZZ",
            "contentTag": "description",
            "class": "sources.MTGovNews",
        },
    },
    required=False,
)
states_to_run = Parameter("states_to_run", default=["ND"])
relevant_title_phrases = Parameter(
    "relevant_title_phrases", default=["covid", "pandemic"]
)
email_list = Parameter("email_list", default=[])
really_send_email = Parameter("really_send_email", default=False)
```

## Notes and caveats

This is currently a very limited prototype that shows scraping 
from a couple RSS feeds. Needed enhancements include things like:

* Support for non-RSS/plain HTML sites
* Add more states
* Support multiple pages of press releases
* More sophisticated relevance detection
* Better email formatting
