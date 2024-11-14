#!/bin/bash

# Start Dgraph Zero
dgraph zero --my=localhost:5080 --wal=/data/zw &

# Wait for Zero to be ready
sleep 10

# Start Dgraph Alpha
dgraph alpha --my=localhost:7080 --zero=localhost:5080 \
    --postings=/data/p --wal=/data/w  --tmp=/data/t \
    --security whitelist=0.0.0.0/0 &

# Start Jupyter notebook
exec start-notebook.sh "$@"