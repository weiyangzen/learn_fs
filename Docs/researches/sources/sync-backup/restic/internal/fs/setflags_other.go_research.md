# sources/sync-backup/restic/internal/fs/setflags_other.go

Purpose: Non-Linux no-op for open-file flag tuning.

Important APIs: `setFlags`.

Control flow and state: Returns nil without modifying the file.

Dependencies and integration: Lets `newLocalFile` call `setFlags` unconditionally across platforms.

Risks: No atime suppression or I/O tuning occurs on these platforms through this hook.

Test signals: No direct tests; behavior is intentionally inert.
