# File Research: sources/os/linux/linux/fs/smb/server/stats.h

Defines ksmbd runtime counters and inline counter helpers.

Key contents:
- Counter indexes for sessions, tree connections, total requests, read bytes, write bytes, and per-request-command counters.
- `struct ksmbd_counters` wraps a `percpu_counter` array when `CONFIG_PROC_FS` is enabled.
- Inline increment/decrement/add/subtract/sum helpers compile to no-ops when procfs support is disabled.
- Per-command request increments are bounds-checked against `KSMBD_COUNTER_MAX_REQS`.

Role in subsystem:
- Lightweight stats abstraction for server accounting without forcing counter overhead when procfs stats are disabled.
