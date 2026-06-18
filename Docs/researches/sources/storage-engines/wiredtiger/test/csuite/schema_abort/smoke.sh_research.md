# sources/storage-engines/wiredtiger/test/csuite/schema_abort/smoke.sh

Purpose: this shell wrapper runs a bounded smoke matrix for `test_schema_abort` as part of `make check`. It gives the heavyweight crash-recovery schema abort test short, deterministic coverage by forcing `-t 10 -T 5` rather than letting the C test choose random timeout and thread counts.

Important APIs and variables: it uses POSIX `sh`, `set -e`, optional positional argument `$1` for a manually supplied binary path, `binary_dir` fallback, and `TEST_WRAPPER` to integrate with the build/test harness. The default binary is `$binary_dir/test_schema_abort`.

Control flow: the script resolves the executable, then runs eighteen invocations. The first group covers default row-store timestamped runs, in-memory mode, compatibility mode, aggressive sweep in compatibility mode, and in-memory plus compatibility. The second group repeats those combinations with `-c` for variable-length column-store. The third group disables timestamps with `-z` across default, sweep, in-memory, and in-memory column-store. The final group enables transactional schema operations with `-x` across default, sweep, in-memory, and in-memory column-store.

State and persistence behavior: the script itself persists no state. Each child test creates and normally removes its own WiredTiger home unless configured otherwise through inherited wrapper/test options.

Dependencies and integration points: it assumes the build system either passes the binary as `$1` or syncs the smoke script next to `test_schema_abort`. `TEST_WRAPPER` may inject sanitizer, timeout, or environment handling.

Risks and test signals: `set -e` makes the first failing variant fail the smoke script. Coverage is intentionally broad but shallow; it does not cover LazyFS or tiered storage, which have separate wrappers or build configurations.
