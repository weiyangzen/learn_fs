# sources/storage-engines/wiredtiger/test/csuite/timestamp_abort/smoke.sh

Purpose: this wrapper runs a short smoke matrix for `test_timestamp_abort`, including backup and live-restore coverage. It keeps the heavy crash-recovery workload bounded with default `-t 10 -T 5` arguments.

Important APIs and variables: it uses POSIX `sh`, `set -e`, `getopts`, `TEST_WRAPPER`, optional `-b` to pass the binary, and optional `-s` to add the C test's timing stress flag. `binary_dir` defaults to the directory containing the script and the default binary is `test_timestamp_abort`.

Control flow: the script builds `default_test_args`, resolves the binary, and runs default, column-store, backup with three iterations, backup plus live restore, in-memory, in-memory column-store, compatibility, compatibility column-store, compatibility plus in-memory, and compatibility plus in-memory column-store variants.

State and persistence behavior: the shell script itself persists nothing. Each underlying C test creates crash/recovery state, backup directories, and sidecar record files in its test home and normally cleans them up on success.

Dependencies and integration points: it integrates with the build's `make check` flow and `TEST_WRAPPER`. It intentionally comments out backup plus compatibility because the C test asserts that compatibility mode is incompatible with backup-related log record changes.

Risks and test signals: the smoke signal is exit status of each invocation. The matrix is broad but still short; long randomized stress, LazyFS, and disaggregated configurations are outside this wrapper.
