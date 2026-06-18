# sources/test-tools/stress-ng/stress-open.c

Purpose: `stress-open.c` implements the `open` stressor, exercising high-volume file descriptor opening and closing across many `open`, `openat`, `openat2`, device, directory, pseudo-terminal, `dup`, procfs, `O_TMPFILE`, `O_DIRECT`, and timestamp update paths.

Important APIs/types/functions: `stress_open_func_t` describes open variants stored in `open_funcs[]`. Wrappers `open_arg2()` and `open_arg3()` time successful opens and call obsolete `futimes` variants. Helpers cover flag permutations (`open_flag_perm()`), `/dev/zero`, `/dev/null`, `O_TMPFILE`, `posix_openpt`, directory and `O_PATH`, invalid `O_CREAT` on a directory, `openat` from cwd or dirfd, Linux `openat2`, `/proc/self/fd`, `dup`, undefined `O_RDONLY | O_TRUNC`, and mode cycling.

Control flow: `stress_open()` creates a temp directory, resolves `open-max` with size and fd limits, mmaps an fd array, optionally forks an `open-fd` child that endlessly opens paths under `/proc/$pid/fd`, computes all flag permutations, synchronizes, and then repeatedly fills the fd array by choosing random open functions until hitting `open_max` or fd exhaustion. It samples fdinfo, periodically syncs, then closes a random fd and tries `close_range()` over the observed min/max range, falling back to individual close and verifying closure with `F_GETFL`.

State and persistence behavior: state includes global `open_count` and `open_perms`, the mmap fd table, optional child process, temp directory/files, cwd changes in `openat` helpers, and metrics for successful open latency. Temporary files are unlinked after each helper and the temp directory is removed at deinit.

Dependencies and integration points: it uses stress-ng filesystem limits, temp-dir helpers, flag permutation generation, `/proc` fdinfo helpers, syscall shims, `close_range`, openat2 headers, futimes shims, fork/kill helpers, and registers as `CLASS_FILESYSTEM | CLASS_OS` with `VERIFY_ALWAYS`.

Risks: many helpers intentionally trigger invalid or platform-specific open combinations, so failures are often expected and retried. `open_with_openat_cwd()` and `open_with_openat2_cwd()` temporarily change cwd and must restore it. `close_range()` over min/max can close fds that were not opened by this stressor if fd ranges overlap in unexpected ways, though the code uses process-local descriptors. High `open-max` values can exhaust memory or descriptors.

Test signals: direct `--open`, `--open-max`, and `--open-fd` should produce nonzero `nanosecs per open` metrics. Good coverage includes kernels with and without `openat2`, filesystems lacking `O_TMPFILE` or `O_DIRECT`, low fd limits, procfs unavailable, and verification that closed descriptors fail `F_GETFL`.
