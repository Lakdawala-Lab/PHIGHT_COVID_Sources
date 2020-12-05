import argparse
import prefect
from prefect import Flow, Parameter, task, unmapped


@task
def scrape(state, state_config, min_date):
    if state not in state_config:
        raise ValueError(f"State {state} was not found in configuration: stopping")
    config = state_config[state]
    logger = prefect.context.get("logger")
    logger.info(f"Running for state {state}")


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

    result = scrape.map(states_to_run, unmapped(state_config), unmapped(min_date))


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
        flow.register(project_name="Default")
