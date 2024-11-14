# Stage 1: Get Dgraph files
FROM dgraph/standalone:v24.0.4 AS dgraph

# Stage 2: Combine with Jupyter
FROM jupyter/minimal-notebook:latest

USER root

# Copy Dgraph binary and related files from Dgraph image
COPY --from=dgraph /usr/local/bin/dgraph /usr/local/bin/

# Create data directory for Dgraph
RUN mkdir -p /data && chown -R ${NB_USER}:${NB_GID} /data

# Create startup script with root
COPY startup.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/startup.sh

# Switch back to notebook user
USER ${NB_USER}

ADD schema.graphql /home/jovyan/
ADD data/ /home/jovyan/data/
ADD episode_importer.py /home/jovyan/
ADD script_importer.py /home/jovyan/
ADD notebook.ipynb /home/jovyan/

# Expose ports
# Jupyter: 8888
# Dgraph Alpha HTTP: 8080
# Dgraph Alpha gRPC: 9080
# Dgraph Zero: 5080
EXPOSE 8888 8080 9080 5080

# Set entrypoint to our startup script
ENTRYPOINT ["/usr/local/bin/startup.sh"]