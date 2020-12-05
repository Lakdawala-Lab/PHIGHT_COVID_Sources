import argparse
import prefect
from prefect import Flow, Parameter, task, unmapped
from web import get_press_releases

@task
def scrape(state, state_config, min_date, relevant_title_phrases):
    if state not in state_config:
        raise ValueError(f"State {state} was not found in configuration: stopping")
    config = state_config[state]
    logger = prefect.context.get("logger")
    logger.info(f"Running for state {state}")

    prs = get_press_releases(config["url"], min_date, relevant_title_phrases)
    for pr in prs:
        logger.info(f"{pr.pubdate} {pr.relevant} {pr.title}")    


with Flow("PHIGHTCOVID_ScrapeBot") as flow:
    min_date = Parameter("min_date", default="2020-11-01", required=True)
    state_config = Parameter(
        "state_config",
        default={
            "MT": {
                "url": "https://news.mt.gov/Home/rss/category/24469/governors-office",
                "type": "RSS"
            }
        },
        required=False,
    )
    states_to_run = Parameter("states_to_run", default=["MT"])
    relevant_title_phrases = Parameter("relevant_title_phrases", default=["covid", "pandemic"])

    result = scrape.map(states_to_run, unmapped(state_config), unmapped(min_date), unmapped(relevant_title_phrases))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI for PHIGHTCOVID ScrapeBot")
    parser.add_argument(
        "action", help="Action to take on Flow: run, register, check",
    )
    parser.add_argument(
        "min_date", help='Minimum date, e.g. "2020-11-01"', nargs="?"
    )
    args = parser.parse_args()
    action = args.action
    if action == "run":
        flow.schedule = None
        flow.run(parameters={"min_date": args.min_date})
    elif action == "register":
        flow.register(project_name="Scraping")
