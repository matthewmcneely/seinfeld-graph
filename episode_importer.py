# load the episode data from the csv file and insert into the Dgraph database

import csv
import sys
from datetime import datetime
from python_graphql_client import GraphqlClient

def load_episodes(client, model):
    
  # Instantiate the client with an endpoint
  if not client:
    client = GraphqlClient(endpoint="http://localhost:8080/graphql")

  # Path to the file containing the episode data
  file_path = 'data/episode_info.csv'

  query = """
  mutation AddSeasonAndEpisode($episodes: [AddEpisodeInput!]!) {
    addEpisode(input: $episodes, upsert: true) {
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
      list = []
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
              },
              "summary": row['Summary']
          }
          list.append(episode)
          count += 1

      if model:
          # Encode all the text in the episode list using the sentence-transformers model
          embeddings = model.encode([item["summary"] for item in list], show_progress_bar=False)
          # Add the embeddings to the list
          list = [dict(list[i], **{"summary_v": embeddings[i].tolist()}) for i in range(len(list))]
      data = client.execute(query=query, variables={"episodes": list})
      if 'errors' in data:
          print(data["errors"])
          print("input data:", episode)
          sys.exit(1)

  end = datetime.now()
  elapsed = end - start

  print(f"{count} episode records inserted in {elapsed.total_seconds():.3} secs")

if __name__ == "__main__":
    load_episodes(None)