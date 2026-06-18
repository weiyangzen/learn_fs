# Research: sources/storage-engines/foundationdb/tests/loopback_cluster/run_cluster.sh

- **Purpose:** Loopback-cluster launcher that prepares a build-directory run area and starts a local cluster using built binaries.
- **Source facts:** 48 lines, 911 bytes, executable=True.
- **Important APIs/types/functions:** Shell commands observed: set, trap, ROOT=`pwd`, function, echo, exit, }, if, usage, fi, BUILD=$1, FDB=${BUILD}/bin/fdbserver, rm, for, DIR=./loopback-cluster-$i, mkdir, PORT_PREFIX=${i}50, CLUSTER_FILE=test$i:testdb$i@127.0.0.1:${PORT_PREFIX}1; plus 10 more. Variable assignments: ROOT, BUILD, FDB, DIR, PORT_PREFIX, CLUSTER_FILE, CLUSTER, LOG, DATA, CLI.
- **Control flow:** Script control constructs: none. It executes sequential shell setup and command-launch steps.
- **State and persistence:** Creates or reuses local cluster runtime directories, configuration files, data/log directories, and process state for a loopback FoundationDB cluster.
- **Dependencies:** Depends on bash, built FoundationDB binaries/config paths, and local filesystem permissions for cluster runtime directories.
- **Integration points:** Used manually or by tests that need a loopback cluster outside deterministic simulation.
- **Risks:** Shell path assumptions and long-running processes can leave stale cluster state if interrupted; environment-specific binary paths must match the build tree.
- **Test signals:** Successful cluster startup and child process exit are the key signals; failures usually appear as shell non-zero exits or cluster logs.
