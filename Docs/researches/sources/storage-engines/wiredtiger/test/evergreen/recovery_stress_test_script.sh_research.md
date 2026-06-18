<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/recovery_stress_test_script.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/recovery_stress_test_script.sh

Purpose: repeatedly runs recovery/abort stress tests across several transaction/logging modes.

Control flow: accepts `times` and optional truncated-log args. Each iteration alternates `test_timestamp_abort -s` timing stress on even iterations, then runs `test_random_abort` and `test_timestamp_abort` in current write-no-sync mode, memory-based txn mode (`-m`), V1 log compatibility (`-C`), and V1 plus memory mode. It also runs `test_truncated_log` with provided args and sleeps ten seconds between iterations.

State and persistence: test binaries create their own homes/logs in the current build tree. The wrapper does not clean state directly.

Dependencies and integration: Evergreen recovery stress tasks run this from a csuite build context containing `random_abort`, `timestamp_abort`, and `truncated_log` subdirectories.

Risks and test signals: strict argument range but usage text references the wrong script name. `set -o errexit` makes the first failing command terminate the wrapper. Optional args are stored as a single variable, so complex quoting is limited.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/recovery_stress_test_script.sh -->
