# sources/storage-engines/foundationdb/packaging/docker/fdb.bash

Purpose: This runtime script starts an `fdbserver` process inside the standard FoundationDB container. It creates the cluster file from environment variables, chooses public IP based on networking mode, and launches the server.

Important functions: `create_cluster_file` writes `FDB_CLUSTER_FILE` from `FDB_CLUSTER_FILE_CONTENTS`, a resolved `FDB_COORDINATOR`, or errors. `create_server_environment` writes `/var/fdb/.fdbenv` with `PUBLIC_IP`, sets default cluster-file contents for self-coordination, and calls `create_cluster_file`.

Control flow: The script creates environment state, sources it, logs the listen address, then execs `fdbserver` with listen/public address, data/log directories, locality IDs from hostname, process class, and `--knob_disable_posix_kernel_aio=1`.

State and persistence behavior: It writes the cluster file, `/var/fdb/.fdbenv`, data under `/var/fdb/data`, and logs under `/var/fdb/logs`. The server process owns ongoing database state.

Dependencies and integration points: It uses `dig`, `hostname`, environment variables from Docker/Compose/Kubernetes, and the `foundationdb` Docker target's entrypoint.

Risks: Coordinator DNS must resolve before startup. Host networking mode always uses `127.0.0.1`, which is suitable for local mapping but not multi-host clusters. Tests should cover cluster-file-content override, coordinator DNS path, host/container modes, missing coordinator error, and server process argument construction.
