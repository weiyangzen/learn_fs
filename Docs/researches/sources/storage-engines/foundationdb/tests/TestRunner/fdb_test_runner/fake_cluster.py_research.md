# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/fake_cluster.py

- **Purpose:** Command wrapper that creates a disposable fake fdb.cluster file for tests that only need cluster-file argument plumbing, not a live database.
- **Source facts:** 88 lines, 2762 bytes, executable=True.
- **Important APIs/types/functions:** Imports: .test_util.random_alphanum_string, argparse.ArgumentParser, argparse.RawDescriptionHelpFormatter, os, pathlib.Path, shutil, subprocess, sys. Classes: ClusterFileGenerator. Top-level functions: main, __init__, __enter__, __exit__, close. Methods: ClusterFileGenerator.__init__, ClusterFileGenerator.__enter__, ClusterFileGenerator.__exit__, ClusterFileGenerator.close. Constants: none. CLI flags/options observed: --output-dir, -o.
- **Control flow:** Executable module: parse command-line arguments, perform setup, run the requested child/test workflow, and convert internal success/failure to process exit status.
- **State and persistence:** launches or inspects child processes (1 subprocess call sites) creates, reads, renames, or removes filesystem artifacts (3 filesystem call sites)
- **Dependencies:** Python imports: .test_util.random_alphanum_string, argparse.ArgumentParser, argparse.RawDescriptionHelpFormatter, os, pathlib.Path, shutil, subprocess, sys; external FoundationDB binaries and shell tools are invoked through subprocess.
- **Integration points:** Integrated as wrapper scripts around test commands that need FDB_CLUSTER_FILE or FDB_CLUSTERS without making each test reimplement cluster setup.
- **Risks:** Failures depend on external FoundationDB binaries, return codes, and trace contents; missing binaries or platform-specific behavior can fail before workload assertions run. The file uses assertions for contract checks, so optimized Python execution would weaken some validation. Randomized names, ports, or workflow choices make collision avoidance and reproducibility dependent on surrounding seed/control logic.
- **Test signals:** Observable signals include returncode, assert; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
