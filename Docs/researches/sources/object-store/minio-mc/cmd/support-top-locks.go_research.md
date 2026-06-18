<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-locks.go -->
# sources/object-store/minio-mc/cmd/support-top-locks.go

Purpose: implements `mc support top locks`, listing active or stale MinIO locks.

Important APIs/types/functions: `supportTopLocksCmd`, `supportTopLocksFlag`, `lockMessage`, `checkSupportTopLocksSyntax`, `mainSupportTopLocks`, `printHeaders`, and `printLocks`.

Control flow: validates one target, enforces registration, sets colors, creates an admin client, calls `TopLocksWithOpts` with hidden `count` and `stale` flags, then prints a table header and each lock message unless JSON output is active. `lockMessage.String` computes elapsed time, detects stale locks by comparing quorum to server list length, and renders a fixed-width row.

State and persistence: read-only command; no local or remote mutation.

Dependencies and integration points: depends on MinIO admin lock API, humanized time formatting, pretty-table utilities in the cmd package, support registration, and global JSON mode.

Risks and test signals: old servers may return zero elapsed, so fallback uses timestamp. Tests should cover stale detection, JSON fields, count/stale option propagation, and table formatting for long resources.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-locks.go -->
