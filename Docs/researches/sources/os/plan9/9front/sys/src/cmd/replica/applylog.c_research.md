# File Research: sources/os/plan9/9front/sys/src/cmd/replica/applylog.c

Applies server change logs to a local replica tree. It reads log records from stdin, compares against local filesystem and client database, detects conflicts, and updates files/database/time cursor.

Handles verbs `d` delete, `a` add, `c` content change, and `m` metadata change. Conflict resolution can prefer server (`-s path`) or client (`-c path`). Path filters intentionally gate filesystem changes while still allowing the replay timestamp to advance only when safe.

Copying uses temp spooling by default, parallel worker processes, remote-file stability checks, optional safe install behavior for binaries, permission fallback, copy-error tracking, and content comparison through temporary snapshots.

Special safety: copies itself to `/tmp/_applylog_*` and re-execs to avoid overwriting the running binary during updates.
