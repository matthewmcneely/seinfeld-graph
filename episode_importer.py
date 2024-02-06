# load the episode data from the csv file and insert into the Dgraph database

import csv
import sys
from datetime import datetime
from python_graphql_client import GraphqlClient

# Instantiate the client with an endpoint
client = GraphqlClient(endpoint="http://localhost:8080/graphql")

# Path to the file containing the episode data
file_path = 'data/episode_info.csv'

query = """
mutation AddSeasonAndEpisode($episode: [AddEpisodeInput!]!) {
  addEpisode(input: $episode, upsert: true) {
    episode {
      id
    }
  }
}
"""

# Read the episode lines and insert one-by-one
start = datetime.now()
count = 0
with open(file_path, 'r', newline='') as file:
    reader = csv.DictReader(file)
    for row in reader:
        airDate = None
        try:
            airDate = datetime.strptime(row["AirDate"], "%B %d, %Y").isoformat()
        except:
            airDate = datetime.strptime(row["AirDate"], "%B %d %Y").isoformat()
            pass
        
        episode = {
            "identifier": row['SEID'],
            "number": int(float(row['EpisodeNo'])),
            "title": row['Title'],
            "airDate": airDate,
            "directors": row['Director'],
            "writers": row['Writers'],
            "season": {
                "number": int(float(row['Season']))
            }
        }
        data = client.execute(query=query, variables={"episode": episode})
        if 'errors' in data:
            print(data["errors"])
            print("input data:", episode)
            sys.exit(1)
        count += 1

end = datetime.now()
elapsed = end - start

print(count, "episode records inserted in", elapsed.microseconds / 1000, "milliseconds")