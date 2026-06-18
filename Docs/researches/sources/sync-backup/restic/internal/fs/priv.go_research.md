# sources/sync-backup/restic/internal/fs/priv.go

Purpose: Non-Windows privilege hook.

Important APIs: `enableProcessPrivileges`.

Control flow and state: Returns nil; no process privileges are adjusted.

Dependencies and integration: Called from `fs_local.go` package init. Provides a common hook for the Windows implementation.

Risks: None beyond being a no-op on non-Windows.

Test signals: No direct tests; local filesystem init depends on this compiling and returning nil.
