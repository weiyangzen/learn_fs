<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fstat.c -->
# sources/test-tools/stress-ng/stress-fstat.c Research

Purpose: implements `fstat`, a filesystem/OS stressor that repeatedly exercises `stat`, `lstat`, `statx`, and `fstat` against entries from a target directory, defaulting to `/dev`.

Important APIs/types/functions: `stress_stat_info_t` caches a path plus ignore bits and access state. `do_not_stat()` filters dangerous paths such as `/dev/watchdog`. `stress_fstat_check_buf()` detects stat buffers left unchanged. `stress_fstat_helper()` performs the actual stat/lstat/statx/fstat calls and intentional invalid calls. With pthread support, `stress_fstat_thread()` and `stress_fstat_threads()` run helper loops concurrently.

Control flow: `stress_fstat()` reads `fstat-dir`, opens it, caches directory entries into a linked list, fills the signal mask, synchronizes, then iterates the cache while work continues. For each path that has not failed all operation classes, it runs helper loops in the main thread and up to four pthreads, increments bogo count, and continues while at least one path remains usable. At the end it frees all cached paths.

State and persistence: cached path nodes are heap state in the worker and are freed at exit. Per-path ignore bits persist only during one stressor invocation to avoid repeated known failures. No files are modified.

Dependencies and integration: depends on pthread helpers, stress-ng statx/lstat/fstat shims, bad-fd generation, scheduling yield, settings, logging, and sync/state transitions. It is VERIFY_ALWAYS.

Risks: the default `/dev` tree can contain special devices whose open/stat behavior differs by privilege; the code avoids opening device files when effective UID is root and blocklists watchdog. Directory contents can change after caching. Threaded helpers share `stress_stat_info_t` ignore/access fields without locks, intentionally trading precision for stress.

Test signals: failures include unchanged stat buffers, unexpected helper errors, and directory-open failures. Useful tests include custom `fstat-dir` paths, non-root versus root behavior, pthread-disabled builds, and statx availability.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fstat.c -->
