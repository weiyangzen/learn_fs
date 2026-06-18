# File Research: sources/os/linux/linux/fs/gfs2/lops.h

Defines the log-operation dispatch interface and declares core low-level journal helpers from `lops.c`.

Key contents:
- Exposes `gfs2_log_ops[]`, the array of registered log operation handlers.
- Declares log-head movement, journal block mapping, log write/submit, buffer pinning, journal-head search, and revoke drain helpers.
- Defines `buf_limit()` and `databuf_limit()` descriptor capacities.
- Provides inline dispatchers for `lo_before_commit`, `lo_after_commit`, `lo_before_scan`, `lo_scan_elements`, and `lo_after_scan`.

This header is the bridge between `log.c` flush/recovery orchestration and individual log operation implementations. Correctness depends on stable operation ordering and every operation tolerating passes/descriptors that do not belong to it.
