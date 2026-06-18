# `sources/test-tools/filebench/utils.c`

Purpose: Provides small portability and resource-limit helpers for Filebench: string allocation, fallback `strlcpy`/`strlcat`, Linux shared-memory limit tuning, and file descriptor limit tuning.

Important APIs and functions: `fb_stralloc()` heap-duplicates a string. `fb_strlcpy()` and `fb_strlcat()` are compiled when platform versions are unavailable. `fb_set_shmmax()` optionally writes a larger `/proc/sys/kernel/shmmax`. `fb_set_rlimit()` optionally raises `RLIMIT_NOFILE` first to the hard limit and then to a fixed large value.

Control flow: These helpers are direct utility calls from parser/runtime code. The resource functions become no-ops when their configure feature macros are absent. On Linux shmmax tuning failure, the code logs a fatal-level warning but returns so execution can continue.

State and persistence: String allocation returns process heap memory. `fb_set_shmmax()` changes a kernel sysctl and explicitly does not restore the original value. `fb_set_rlimit()` changes process resource limits for the current Filebench process.

Dependencies and integration: Depends on `filebench_log()`, `filebench.h`, configure macros, `parsertypes.h`, libc, `/proc/sys/kernel/shmmax`, and `setrlimit()`. The utilities smooth portability across Solaris and non-Solaris platforms.

Risks and test signals: Fallback `strlcpy`/`strlcat` return the copied length plus NUL, not the full source length semantics of BSD `strlcpy`/`strlcat`, so callers expecting truncation detection may be misled. `fb_stralloc(NULL)` would crash. Sysctl writes need privilege and are global. Tests should cover truncation behavior, no-op builds without feature macros, unprivileged shmmax handling, and fd limit changes.
