# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/tmp_multi_cluster.py

- **Purpose:** CLI wrapper that starts multiple temporary clusters, exposes their cluster files through FDB_CLUSTERS, runs a child command, and then closes all clusters.
- **Source facts:** 92 lines, 2843 bytes, executable=True.
- **Important APIs/types/functions:** Imports: .cluster_args.CreateTmpFdbClusterArgParser, .tmp_cluster.TempCluster, os, subprocess, sys. Classes: none. Top-level functions: main. Methods: none. Constants: none. CLI flags/options observed: --clusters, -c.
- **Control flow:** Executable module: parse command-line arguments, perform setup, run the requested child/test workflow, and convert internal success/failure to process exit status.
- **State and persistence:** launches or inspects child processes (1 subprocess call sites)
- **Dependencies:** Python imports: .cluster_args.CreateTmpFdbClusterArgParser, .tmp_cluster.TempCluster, os, subprocess, sys; external FoundationDB binaries and shell tools are invoked through subprocess.
- **Integration points:** Integrated as wrapper scripts around test commands that need FDB_CLUSTER_FILE or FDB_CLUSTERS without making each test reimplement cluster setup.
- **Risks:** Failures depend on external FoundationDB binaries, return codes, and trace contents; missing binaries or platform-specific behavior can fail before workload assertions run.
- **Test signals:** Observable signals include returncode; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
