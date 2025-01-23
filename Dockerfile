FROM neo4j
COPY extension_script.sh /extension_script.sh
# Possibilita a montagem do diretório em /import
# https://neo4j.com/docs/operations-manual/current/docker/mounting-volumes/#docker-volumes-mount-points
RUN echo "============== ${NEO4J_HOME} ====================="
RUN ln -s /import "${NEO4J_HOME}"/import
ENV EXTENSION_SCRIPT=/extension_script.sh

# Possibilita o uso do apoc-full
# https://neo4j.com/docs/apoc/current/installation/
ENV NEO4J_apoc_export_file_enabled=true
ENV NEO4J_apoc_import_file_enabled=true
ENV NEO4J_apoc_import_file_use__neo4j__config=true
