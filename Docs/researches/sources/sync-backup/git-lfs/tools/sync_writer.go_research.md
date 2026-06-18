# sources/sync-backup/git-lfs/tools/sync_writer.go

Purpose: wrapper that synchronizes writes when the underlying writer supports `Sync`, and closes when it supports `io.Closer`.

Important APIs/types/functions: `SyncWriter`, `NewSyncWriter`, `Write`, and `Close`.

Control flow: constructor detects optional `Sync()` and `Close()` methods and installs no-op fallbacks. `Write` delegates to the wrapped writer and calls sync only on successful write.

State and persistence: holds function pointers for optional behavior; can force data flushes for file-backed progress logs.

Dependencies and integration points: used by `tq.Meter` for `GIT_LFS_PROGRESS` logging.

Risks: `Write` discards the byte count and cannot report short writes unless the underlying writer returns an error. Sync after every write can be expensive.

Test signals: no direct test in this subset.
