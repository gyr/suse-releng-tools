#!/usr/bin/env python3

from argparse import ArgumentParser
import requests

QUERY = """
query {{
  binaries(name_Iexact:"{}") {{
    edges {{
      node {{
        channelsources {{
          edges {{
            node {{
              channel {{
                name
              }}
              package {{
                name
              }}
              project {{
                name
              }}
            }}
          }}
        }}
      }}
    }}
  }}
}}
"""
SMELT_API = "https://smelt.suse.de/graphql/"

def get_binary_info(binary):
    query = {"query": QUERY.format(binary)}
    results = requests.post(SMELT_API, query).json()

    for bin_result in results["data"]["binaries"]["edges"]:
        for result in bin_result["node"]["channelsources"]["edges"]:
            yield (result["node"]["channel"]["name"],
                   result["node"]["project"]["name"],
                   result["node"]["package"]["name"])

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("binaries", metavar="binary", help="The binary names", nargs="+")
    options = parser.parse_args()


    for binary in options.binaries:
        print("{}:".format(binary))
        for chan, proj, pack in  get_binary_info(binary):
            print(" {}: {}/{}".format(chan, proj,pack))
