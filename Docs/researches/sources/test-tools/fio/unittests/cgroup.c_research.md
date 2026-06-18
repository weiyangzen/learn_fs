# sources/test-tools/fio/unittests/cgroup.c

Purpose: CUnit tests for fio cgroup helper behavior around long paths. The file provides local stubs for fio allocation, logging, and semaphore symbols, includes `../cgroup.c` directly, and registers cgroup-specific tests on Linux/Android.

Important APIs/functions: `test_path_join()` builds dynamic path strings. `test_get_cgroup_root_long_path()` verifies `get_cgroup_root()` can concatenate a long cgroup name under a mount path and preserve lengths over 64 bytes without setting `td.error`. `test_write_int_to_file_long_path()` creates a temporary long directory, calls `write_int_to_file()`, then reads back `blkio.weight`.

Control flow/state: tests allocate temporary memory and directories under `/tmp/fio-cgroup-XXXXXX`, assert each operation, then unlink/rmdir cleanup. Stubbed `smalloc`, `scalloc`, `sfree`, and `smalloc_strdup` map to libc.

Dependencies/integration: uses CUnit, fio `thread_data`, direct inclusion of production cgroup code, libc filesystem APIs, and platform guards from `unittest.h`.

Risks/test signals: direct inclusion is fragile to new external symbols in `cgroup.c`. The long-path tests are good regression signals for fixed-size buffer truncation. Cleanup only runs after successful fatal assertions, so failures can leave temp directories.
