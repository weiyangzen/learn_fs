<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/checkpoint_stress_test.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/checkpoint_stress_test.sh

Purpose: runs `test_checkpoint` as a concurrent stress workload from the CMake `test/checkpoint` directory. It accepts `tiered`, `times`, `no_of_procs`, `wt_config`, and `timestamp_config`, exports a low-durability `WIREDTIGER_CONFIG`, and builds a command that runs random test mode with high operation/key counts. When `tiered` is enabled it appends `-PT`.

Control flow: for each outer iteration it launches `no_of_procs` background `nohup` jobs with distinct `WT_TEST.$i.$t` homes, then waits for each child via `wait -n`. On failure it filters noisy checkpoint/verification/thread-start lines from all `nohup.out.*` files, remembers the failing exit code, and exits after collecting process results.

State and persistence: creates test home directories and `nohup.out` logs in the current build directory; it does not clean them. It relies on inherited binaries and path context.

Dependencies and integration: called by Evergreen checkpoint stress task definitions in `test/evergreen.yml`; requires `test_checkpoint` and shell support for `wait -n`.

Risks and test signals: argument count is strict, and the command is assembled with `eval`, so quoting depends on Evergreen-supplied config expansions. Success is child exit status; logs become the main diagnostic signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/checkpoint_stress_test.sh -->
