# sources/sync-backup/bup/wvtest-bup.sh

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/wvtest-bup.sh -->
## sources/sync-backup/bup/wvtest-bup.sh

Purpose: `wvtest-bup.sh` is a tiny Bup-specific wrapper around the generic shell test harness. It sources `wvtest.sh`, captures the repository top directory, and provides helpers for creating temporary test directories and mount points under stable Bup test paths.

Important APIs and functions: `_wvtop="$(pwd -P)"` records the physical working directory at source time. `wvmktempdir` creates `$_wvtop/test/tmp` and returns a `mktemp -d` directory named from the current script. `wvmkmountpt` does the same under `$_wvtop/test/mnt`, intended for filesystem or FUSE mount tests.

Control flow: callers source this file from Bash tests. Sourcing first loads `wvtest.sh`, then initializes `_wvtop`. Each helper derives `script_name` from `$0`, ensures the parent directory exists, then calls `mktemp -d` with a per-script prefix. Any mkdir or mktemp failure exits the test immediately through `|| exit $?`.

State and persistence: it persists temporary directories under `test/tmp` and `test/mnt` in the source tree. It does not register cleanup itself, so test suites or callers must clean these directories.

Dependencies and integration points: depends on the Bup `wvtest.sh` assertion framework, POSIX `mkdir`, `mktemp`, `basename`, and the test suite convention that tests run from the Bup top directory. It integrates with mount-oriented tests by keeping mount points under a known tree.

Risks: if sourced from the wrong current directory, `_wvtop` points to the wrong root and helpers create directories outside the intended test tree. Mount-point directories may require special cleanup if a test fails while mounted. `$0` can be less descriptive for sourced scripts or unusual shell launchers.

Test signals: successful use returns unique directories. Failure is intentionally hard because temp directory creation is foundational for isolation.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/wvtest-bup.sh -->
