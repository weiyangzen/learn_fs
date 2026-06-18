## sources/sync-backup/syncthing/lib/osutil/atomic_unix_test.go

Purpose: Unix-specific test ensuring atomic temp files start with secure permissions.

Important test: `TestTempFilePermissions` creates an atomic writer, stats the temp file before close, and verifies mode `0600`.

Control flow and state: the test observes the temporary file directly through `w.next.Name()` before the final rename.

Dependencies and integration points: relies on Unix permission semantics and `CreateAtomic`/`TempFile`.

Risks: unavailable on non-Unix platforms; umask or filesystem semantics could affect expectations if temp creation changes.

Test signals: security-relevant coverage for temp file permissions.
