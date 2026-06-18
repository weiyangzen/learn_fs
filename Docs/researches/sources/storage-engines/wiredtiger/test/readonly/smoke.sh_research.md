# sources/storage-engines/wiredtiger/test/readonly/smoke.sh

Purpose: smoke runner for the readonly test executable.

Important APIs and control flow: installs a trap that restores user write permission on `WT_*` paths for normal exit and common signals, enables `set -e`, and runs `$TEST_WRAPPER ./t`.

State and persistence behavior: the script itself mutates permissions during cleanup only. Runtime database directories are created by `./t`.

Dependencies and integration points: depends on POSIX shell, `chmod`, the test executable named `t`, and the test harness-provided `TEST_WRAPPER`.

Risks: the broad `chmod -R u+w WT_*` pattern can affect unrelated matching directories in the working directory. It assumes a shell/glob environment compatible with the test layout.

Test signals: zero exit status from `./t` and cleanup trap execution are the expected smoke signals.
