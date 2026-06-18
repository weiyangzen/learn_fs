# sources/sync-backup/restic/internal/fs/file_windows_test.go

Purpose: Windows-only test for delete-on-close temporary files.

Important APIs: `TestTempFile`.

Control flow and state: Creates two temp files with the same prefix, verifies distinct names and existence while open, closes both, then verifies the paths no longer exist.

Dependencies and integration: Tests `fs.TempFile` from external package perspective (`fs_test`), covering Windows-specific `CreateFile` flags.

Risks: Does not inspect temporary-file attributes directly; behavior is inferred from existence and deletion.

Test signals: Confirms collision avoidance and delete-on-close semantics for simultaneous temp files.
