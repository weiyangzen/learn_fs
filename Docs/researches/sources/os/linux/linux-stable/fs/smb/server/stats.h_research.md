# File Research: sources/os/linux/linux-stable/fs/smb/server/stats.h

## Summary
Defines ksmbd server counters and inline counter operations, enabled when `CONFIG_PROC_FS` is available and compiled to no-ops otherwise.

## Main Responsibilities
- Enumerate counters for sessions, tree connections, requests, read/write bytes, and per-command request counts.
- Define `struct ksmbd_counters` as an array of percpu counters.
- Provide inline increment/decrement/add/subtract/sum helpers.
- Bound per-command request counters with `KSMBD_COUNTER_MAX_REQS`.

## Cross-File Interactions
Read/write paths in `vfs.c` update byte counters; request dispatch paths can update request counters; proc/debug code can report sums.

## Risks
Counter indexes must match allocation size. The no-op fallback means code must not rely on these helpers for correctness when procfs is disabled.
