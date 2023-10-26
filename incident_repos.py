#!/usr/bin/env python3

from argparse import ArgumentParser
import requests

QUERY = """
query {{
  incidents(incidentId:{}) {{
    edges {{
      node {{
        repositories {{
          edges {{
            node {{
              name
            }}
          }}
        }}
      }}
    }}
  }}
}}
"""
SMELT_API = "https://smelt.suse.de/graphql/"

def get_incident_repos(iid):
    query = {"query": QUERY.format(iid)}
    results = requests.post(SMELT_API, query).json()

    incs_repos = [i["node"]["repositories"]["edges"] for i in results["data"]["incidents"]["edges"]]
    repos = set()
    for inc_repos in incs_repos:
        repos.update({s["node"]["name"] for s in inc_repos})

    return repos

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("incidents", metavar="incident", help="The incident numbers", nargs="+", type=int)
    options = parser.parse_args()


    for iid in options.incidents:
        print("{}:".format(iid))
        for repo in get_incident_repos(iid):
            print("  * {}".format(repo))
