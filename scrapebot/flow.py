import argparse
import prefect
import requests
import pendulum
from prefect import Flow, Parameter, task, unmapped
from web import get_press_releases


@task
def scrape(state, state_config, min_date, relevant_title_phrases):
    if state not in state_config:
        raise ValueError(f"State {state} was not found in configuration: stopping")
    config = state_config[state]
    logger = prefect.context.get("logger")
    logger.info(f"Running for state {state}")

    prs = get_press_releases(config, min_date, relevant_title_phrases)
    if prs:
        for pr in prs:
            logger.info(f"{pr.pubdate} {pr.relevant} {pr.title}")

        return [pr for pr in prs if pr.relevant]
    else:
        logger.info(f"Did not find any press releases for {state}. Exiting")
        return []


@task
def send_email(relevant_prs, email_list, really_send_email):
    logger = prefect.context.get("logger")
    # logger.info(relevant_prs)
    text = '''
    <html>
    <head>
    <style>
    #customers {
        font-family: Arial, Helvetica, sans-serif;
        border-collapse: collapse;
        width: 100%;
        }

    #customers td, #customers th {
        border: 1px solid #ddd;
        padding: 8px;
        }

    #customers tr:nth-child(even){background-color: #f2f2f2;}

    #customers tr:hover {background-color: #ddd;}

    #customers th {
        padding-top: 12px;
        padding-bottom: 12px;
        text-align: left;
        background-color: #4CAF50;
        color: white;
        }
    </style>
    </head>
    <body>
    '''
    RSS_States = ["Alabama", "Delaware", "DC", "Hawaii", "Kansas", 
                  "Maryland", "Mississippi", "Montana", "New Mexico", 
                  "New York", "North Carolina", "Pennsylvania", 
                  "Rhode Island", "Utah", "Vermont"]
    for list_for_state in relevant_prs:
        text += "<b>" + RSS_States.pop(0) + "</b> <br>"
        state_table = '''
                        <table id = \"customers\">
                        <tr>
                            <th>Date</th>
                            <th>Title</th>
                            <th>Link</th>
                        </tr>
                      '''
        for pr in list_for_state:
            state_table += '''
                <tr>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                </tr>
            '''%(f"{str(pr.pubdate)[:10]}", f"{pr.title}", f"{pr.link}")
        #f"{str(pr.pubdate)[:10]} {pr.title} {pr.link}"
        text += state_table + "</table>"
    
    text += '''
            </body>
            </html>
            '''
    
    logger.info(f"Preparing body of email as:\n{text}")
    api_key = prefect.client.Secret("MAILGUN_API_KEY").get()
    if not really_send_email:
        logger.info(
            f"NOT sending email since really_send_email parameter is {really_send_email}"
        )
    else:
        response = requests.post(
            "https://api.mailgun.net/v3/sandboxaa439a4916b44776a48d99842c6bcf9d.mailgun.org/messages",
            auth=("api", api_key),
            data={
                "from": "PHIGHTCOVID <mailgun@sandboxaa439a4916b44776a48d99842c6bcf9d.mailgun.org>",
                "to": email_list,
                "subject": f"PHIGHT COVID Relevant Press Releases {str(pendulum.today())[:10]}",
                "html": text
            },
        )
        logger.info(f"Response from mail service: {str(response)}")


with Flow("PHIGHTCOVID_ScrapeBot") as flow:
    min_date = Parameter("min_date", default="2020-11-01", required=True)
    state_config = Parameter(
        "state_config",
        default={
            # Alabama
            "AL": {
                "url": "https://governor.alabama.gov/feed/",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss ZZ",
                "contentTag": "description",
                "class": "sources.MTGovNews",
            },
            # Delaware
            "DE": {
                "url": "https://news.delaware.gov/tag/coronavirus/feed/",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss ZZ",
                "contentTag": "description",
                "class": "sources.MTGovNews",
            },
            # District of Columbia
            "DC": {
                "url": "https://coronavirus.dc.gov/node/%2A/newsroom",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss ZZ",
                "contentTag": "description",
                "class": "sources.MTGovNews",
            },
            # Hawaii
            "HI": {
                "url": "https://hawaiicovid19.com/feed/",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss ZZ",
                "contentTag": "description",
                "class": "sources.MTGovNews",
            },
            # Kansas
            "KS": {
                "url": "https://covid.ks.gov/feed/",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss ZZ",
                "contentTag": "description",
                "class": "sources.MTGovNews",
            },
            # Maryland
            "MD": {
                "url": "https://governor.maryland.gov/category/press-releases/feed/",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss z",
                "contentTag": "content:encoded",
                "class": "sources.MTGovNews",
            },
            # Mississippi
            "MS": {
                "url": "https://governorreeves.ms.gov/feed/",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss z",
                "contentTag": "content:encoded",
                "class": "sources.MTGovNews",
            },
            # Motanta
            "MT": {
                "url": "https://news.mt.gov/Home/rss/category/24469/governors-office",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss z",
                "contentTag": "content:encoded",
                "class": "sources.MTGovNews",
            },
            # New Mexico
            "NM": {
                "url": "https://cv.nmhealth.org/feed/",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss ZZ",
                "contentTag": "description",
                "class": "sources.MTGovNews",
            },
            # New York
            "NY": {
                "url": "https://www.governor.ny.gov/rss.xml",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss ZZ",
                "contentTag": "description",
                "class": "sources.MTGovNews",
            },
            # North Carolina
            "NC": {
                "url": "https://www.nc.gov/aggregator/rss/1",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss ZZ",
                "contentTag": "description",
                "class": "sources.MTGovNews",
            },
            # North Dakota
            "ND": {
                "url": "https://www.governor.nd.gov/rss/news",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss ZZ",
                "contentTag": "description",
                "class": "sources.MTGovNews",
            },
            # Pennsylvania
            "PA": {
                "url": "https://www.governor.pa.gov/feed/",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss ZZ",
                "contentTag": "description",
                "class": "sources.MTGovNews",
            },
            # Rhode Island
            "RI": {
                "url": "https://covid.ri.gov/press-releases.xml",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss ZZ",
                "contentTag": "description",
                "class": "sources.MTGovNews",
            },
            # Utah
            "UT": {
                "url": "https://governor.utah.gov/feed/",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss ZZ",
                "contentTag": "description",
                "class": "sources.MTGovNews",
            },
            # Vermont
            "VT": {
                "url": "https://governor.vermont.gov/press.xml",
                "type": "RSS",
                "pubdateFormat": "ddd, DD MMM YYYY HH:mm:ss ZZ",
                "contentTag": "description",
                "class": "sources.MTGovNews",
            },
        },
        required=False,
    )
    states_to_run = Parameter("states_to_run", default=["AL", "DE", "DC", "HI", "KS", "MD", "MS", "MT", "NM", "NY",
                                                        "NC", "PA", "RI", "UT", "VT"])
    relevant_title_phrases = Parameter(
        "relevant_title_phrases", default=["covid", "pandemic", "Coronavirus", "covid-19", "vaccines"]
    )
    email_list = Parameter("email_list", default=['zongyuay@andrew.cmu.edu', 'phightcovid@gmail.com'])
    really_send_email = Parameter("really_send_email", default=True)

    relevant_prs = scrape.map(
        states_to_run,
        unmapped(state_config),
        unmapped(min_date),
        unmapped(relevant_title_phrases),
    )

    send_email(relevant_prs, email_list, really_send_email)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI for PHIGHTCOVID ScrapeBot")
    parser.add_argument(
        "action",
        help="Action to take on Flow: run, register, check",
    )
    parser.add_argument("min_date", help='Minimum date, e.g. "2020-11-01"', nargs="?")
    args = parser.parse_args()
    action = args.action
    if action == "run":
        flow.schedule = None
        flow.run(parameters={"min_date": args.min_date})
    elif action == "register":
        flow.register(project_name="Scraping")
