# sources/storage-engines/foundationdb/packaging/docker/samples/python/app/Dockerfile

Purpose: This Dockerfile builds the Python Flask sample application image for FoundationDB. It installs FDB client libraries/tools and optional multiversion client libraries.

Important operations: It copies `libfdb_c.so`, `fdbcli`, and `create_cluster_file.bash` from the FoundationDB image stage, installs `dnsutils` and `curl`, downloads additional client libraries listed in `FDB_ADDITIONAL_VERSIONS`, installs Python requirements, copies `start.bash` and `server.py`, and sets Flask environment variables.

Control flow: Build-time loops over additional versions and writes them under `/usr/lib/fdb-multiversion`, with `FDB_NETWORK_OPTION_EXTERNAL_CLIENT_DIRECTORY` pointing there.

State and persistence behavior: The image persists the Python app, FDB client library/tools, and multiversion client libraries. Runtime state is in FDB.

Dependencies and integration points: It integrates with the FoundationDB Docker image, the Python binding requirements file, Flask server, and Compose environment.

Risks: The additional client library URL uses `FDB_WEBSITE` defaulting to `https://www.foundationdb.org` download paths, which differs from the GitHub release pattern elsewhere. Tests should build with no additional versions and with one version, then run the Flask counter routes against compose.
