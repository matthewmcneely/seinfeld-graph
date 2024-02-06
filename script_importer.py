# load the script data from the csv file and insert into the Dgraph database

import re
import csv
import sys
import json
from datetime import datetime
from python_graphql_client import GraphqlClient

client = GraphqlClient(endpoint="http://localhost:8080/graphql")

# Path to the file containing the script data
file_path = 'data/scripts.csv'

query = """
mutation AddLine($input: [AddLineInput!]!) {
  addLine(input: $input) {
    line {
      id
    }
  }
}
"""

# Read lines for each episode and insert them in bulk, one season at a time
start = datetime.now()
count = 0
skipped = 0
character_episode_map = {}
with open(file_path, 'r', newline='') as file:
    reader = csv.DictReader(file)
    current_season = 1.0
    list = []
    for row in reader:
        season = float(row['Season'])
        if season != current_season:
            current_season = season
            data = client.execute(query=query, variables={"input": list})
            if 'errors' in data:
                print(data["errors"])
                sys.exit(1)
            list = []
            print("season", current_season-1.0, "inserted")
        
        characters = re.findall(r'\b[A-Z]+\b', row['Character'])
        if len(characters) == 0:
            skipped += 1
            continue
        for character in characters:
          line = {
              "text": row['Dialogue'],
              "character": {
                  "name": character
              },
              "episode": {
                  "identifier": row['SEID']
              }
          }
          # store the character-episode mapping for stich-up (this is the one inverse edge that needs to be updated this way)
          if not row["SEID"] in character_episode_map:
             character_episode_map[row['SEID']] = []
          character_episode_map[row['SEID']].append({
              "name": character}
          )
          list.append(line)
          count += 1

query = """
mutation UpdateEpisode($input: UpdateEpisodeInput!) {
  updateEpisode(input: $input) {
    numUids
  }
} 
"""

print("updating episodes with characters...")
for key in character_episode_map:
  data = client.execute(query=query, variables={"input": {"filter": {"identifier": {"eq": key}}, "set": {"characters": character_episode_map[key]}}})
  if 'errors' in data:
    print(data["errors"])
    sys.exit(1)  

end = datetime.now()
elapsed = end - start
print(count, "lines inserted in", elapsed.microseconds / 1000, "milliseconds")
print(skipped, "lines skipped (no character found)")