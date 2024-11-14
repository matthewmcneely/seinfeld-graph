# A Seinfeld Graph

This repo contains code to create a GraphQL-based network graph of the Seasons, Episodes and Lines by Character from the popular sitcom "Seinfeld".

The graph is managed using [Dgraph](https://dgraph.io), an open-source horizontally-scalable native graph database that exposes a complete GraphQL API.

### Requirements

* make
* python 3.10+
* docker-compose
* python-graphql-client (`pip install python-graphql-client`)

### Running

After cloning...

1. `make up`
1. in a separate terminal window: `make schema import`

Alternatively, you can run everything (including a self-contained Dgraph cluster) with:

```make run-image```

The containerized Jupyter Lab will have a notebook which demos the Dgraph Vector Embeddings search functionality.

### Stats

* 9 Seasons
* 174 Episodes
* 910 Characters
* 56,149 Lines

### Sample Queries

Find all lines with the term 'marble' (who doesn't like a nice marble rye?)
```graphql
query {
  queryLine(filter: { text: { anyofterms: "marble" } }) {
    text
    character {
      name
    }
    episode {
      identifier
      title
    }
  }
}
```

Find all the episodes in which MORTY (Jerry's Dad) appears, and his lines in each Episode:
```graphql
query {
  queryEpisode @cascade {
    identifier
    _: characters(filter: { name: { eq: "MORTY" } }) {
      name @skip(if: true)
    }
    lines {
      text
      _: character(filter: { name: { eq: "MORTY" } }) {
        id @skip(if: true)
      }
    }
  }
}

```

### License

This work is licensed under the Creative Commons BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/)

Seinfeld Data was obtained from https://www.kaggle.com/datasets/thec03u5/seinfeld-chronicles/data, which also has the same CC BY-SA 4.0 license.



