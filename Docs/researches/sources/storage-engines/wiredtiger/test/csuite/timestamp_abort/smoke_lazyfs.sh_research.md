# sources/storage-engines/wiredtiger/test/csuite/timestamp_abort/smoke_lazyfs.sh

Purpose: this wrapper runs `test_timestamp_abort` with LazyFS enabled, using a longer bounded timeout than the main smoke matrix. It is targeted at crash recovery when filesystem writes may be lost from the lazy cache.

Important APIs and variables: it uses POSIX `sh`, `set -e`, `getopts`, optional `-s` for timing stress, optional `-b` for the binary path, `binary_dir` fallback, and `TEST_WRAPPER`. The default arguments are `-t 20 -T 5`.

Control flow: the script resolves the test binary, then runs two invocations: LazyFS default and LazyFS plus compatibility mode. It uses the C test's uppercase `-L` option, which explicitly enables LazyFS.

State and persistence behavior: state is owned by the underlying C test: records files, WiredTiger home, backups when configured elsewhere, and LazyFS cache state. The wrapper only sequences two invocations.

Dependencies and integration points: it requires a build and environment that support LazyFS. It shares binary-location conventions with the normal smoke wrapper and depends on `TEST_WRAPPER` for test harness concerns.

Risks and test signals: the pass signal is both invocations exiting successfully. The script does not cover backup/live-restore LazyFS combinations; it focuses on core timestamp abort recovery with and without compatibility mode.
