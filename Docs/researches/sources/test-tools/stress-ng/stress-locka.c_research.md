# sources/test-tools/stress-ng/stress-locka.c

Purpose: implements `locka`, an advisory file-lock contention stressor that has parent and child processes repeatedly acquire random byte-range write locks on a shared file and recycle old lock records.

Important APIs/types/functions: `stress_locka_info_t` stores offset, length, and pid for acquired locks. `stress_locka_info_list_t locka_infos` tracks active, tail, free-list, and length. `stress_locka_info_new()`, `stress_locka_info_head_remove()`, and `stress_locka_info_free()` manage records. `stress_locka_contention()` performs random `F_SETLK` lock attempts and unlocks older ranges via `stress_locka_unlock()`.

Control flow: `stress_locka()` creates a shared temp directory, opens a lock file, writes 1 MiB of zero-filled content, reports disk usage, sync-starts, forks a child pinned toward the parent CPU, and both parent and child run `stress_locka_contention()` on the inherited fd. Each contention loop limits active records to 1024 by unlocking the oldest, chooses random length and offset, attempts nonblocking `F_SETLK`, records successful locks, and increments bogo ops. Teardown kills the child, frees lock records, closes and unlinks the file, and removes the directory.

State and persistence behavior: the file and directory are temporary. Advisory locks live in kernel state associated with processes and fds. The active-lock list is process-local, so parent and child do not share lock bookkeeping.

Dependencies and integration points: compile-gated on POSIX `fcntl` lock commands and lock types. Uses stress-ng affinity, fork retry, kill helpers, temp filesystem, CPU discovery, scheduler settings, and process state. Registered as `CLASS_FILESYSTEM | CLASS_OS`.

Risks: because locks are advisory and process-scoped, inherited fd semantics and parent/child interactions are kernel-dependent. The file directory creation intentionally races across instances and tolerates `EEXIST`. Failed lock attempts are ignored to maximize contention.

Test signals: run multiple workers with `--verify`, confirm no stale lock file/directory, child is reaped, bogo ops advance under contention, and failures are limited to resource/fork or unexpected `fcntl` unlock errors.
