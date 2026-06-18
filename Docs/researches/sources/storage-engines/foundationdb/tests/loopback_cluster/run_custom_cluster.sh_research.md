# Research: sources/storage-engines/foundationdb/tests/loopback_cluster/run_custom_cluster.sh

- **Purpose:** Customizable loopback cluster launcher for running fdbmonitor/fdbserver from explicit or build-derived paths.
- **Source facts:** 236 lines, 6880 bytes, executable=True.
- **Important APIs/types/functions:** Shell commands observed: set, SERVER_COUNT=1, readonly, STATELESS_COUNT=4, REPLICATION_COUNT=1, LOGS_COUNT=8, STORAGE_COUNT=16, KNOBS=, LOGS_TASKSET=, STATELESS_TASKSET=, STORAGE_TASKSET=, STORAGE_TYPE=ssd, LOGROUTER_COUNT=0, DUMP_PIDS=, PIDS=(), function, echo, printf; plus 79 more. Variable assignments: SERVER_COUNT, STATELESS_COUNT, REPLICATION_COUNT, LOGS_COUNT, STORAGE_COUNT, KNOBS, LOGS_TASKSET, STATELESS_TASKSET, STORAGE_TASKSET, STORAGE_TYPE, LOGROUTER_COUNT, DUMP_PIDS, PIDS, status, BUILD, FDB, replication, LOOPBACK_DIR; plus 3 more.
- **Control flow:** Script control constructs: none. It executes sequential shell setup and command-launch steps.
- **State and persistence:** Creates or reuses local cluster runtime directories, configuration files, data/log directories, and process state for a loopback FoundationDB cluster.
- **Dependencies:** Depends on bash, built FoundationDB binaries/config paths, and local filesystem permissions for cluster runtime directories.
- **Integration points:** Used manually or by tests that need a loopback cluster outside deterministic simulation.
- **Risks:** Shell path assumptions and long-running processes can leave stale cluster state if interrupted; environment-specific binary paths must match the build tree.
- **Test signals:** Successful cluster startup and child process exit are the key signals; failures usually appear as shell non-zero exits or cluster logs.
