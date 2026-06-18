## sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_sendfile.go

Purpose: Linux/Solaris copy-range backend using `sendfile`.

Important APIs/types/functions: Registers `CopyRangeMethodSendFile`; `copyRangeSendFile` copies bytes from source fd to destination fd with explicit source offset.

Control flow: Ensures destination size, records and restores current destination offset, seeks destination to requested offset, loops `syscall.Sendfile`, treats zero-without-error as EOF, retries `EAGAIN`, and subtracts positive byte counts.

State and persistence: Writes destination bytes and temporarily changes destination file offset, restoring it before return.

Dependencies and integration points: Linux/Solaris build tags; copy-range registry and descriptor helper.

Risks: Offset restoration is important for callers sharing file handles. Sendfile support and behavior differ across filesystems/platforms.

Test signals: No direct tests in subset.
