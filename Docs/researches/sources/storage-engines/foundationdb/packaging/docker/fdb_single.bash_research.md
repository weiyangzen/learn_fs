# sources/storage-engines/foundationdb/packaging/docker/fdb_single.bash

Purpose: This variant starts a single-node FoundationDB container and automatically configures it as `single memory`. It is useful for demos and local samples.

Important functions: It shares `create_cluster_file` and `create_server_environment` logic with `fdb.bash`, adds `start_fdb` to launch `fdbserver` in the background, and `configure_fdb_single` to run `fdbcli --exec 'configure new single memory'` followed by `status`.

Control flow: Strict mode and job control are enabled. The script starts the server, waits five seconds, configures the database, then foregrounds the server job so the container stays alive.

State and persistence behavior: It writes the same cluster/data/log/env files as `fdb.bash` and persists a configured single-memory database in the data volume.

Dependencies and integration points: It depends on `fdbserver`, `fdbcli`, DNS tools, and container environment variables. Samples or developers can use it when they want self-configuration.

Risks: Fixed sleep can race slow startup, and repeated runs against an already configured database may fail the `configure new` step. Tests should run fresh and existing-data containers, verify foreground signal handling, and check cluster file creation paths.
