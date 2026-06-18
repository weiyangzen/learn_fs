# sources/test-tools/strace/tests/newfstatat.c

Purpose: is a thin architecture/test alias for the generic `fstatat.c` test. It compiles the shared implementation under the `newfstatat` test name.

Important APIs, types, and helpers: inherits from `fstatat.c`, which exercises the `newfstatat`/`fstatat`-style syscall decoder, stat structures, path arguments, directory fd handling, and flag decoding.

Control flow: no local runtime logic exists; the preprocessor includes `fstatat.c` directly.

State and persistence: local file adds no state. Any temporary files or paths are managed by the included shared test.

Dependencies and integration points: integrates with strace’s syscall-name matrix where the same stat-at behavior may be exposed through architecture-specific syscall names. Build-system selection decides this source’s role.

Risks and edge cases: all behavior depends on the included file. If `fstatat.c` changes assumptions about syscall names or wrappers, this alias test may need expected-output updates.

Test signals: same as the shared fstat-at test, but attributed to the `newfstatat` source/test binary.
