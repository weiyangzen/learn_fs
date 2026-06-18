# sources/sync-backup/kopia/repo/maintenance/helper_test.go

Purpose: exposes unexported maintenance helpers to the external `maintenance_test` package.

Important APIs/types/functions: exported test-only wrapper `ExtendBlobRetentionTime`.

Control flow: the wrapper delegates directly to `extendBlobRetentionTime`.

State/persistence behavior: same as the underlying retention task; this file itself has no state.

Dependencies/integration: lets black-box tests call retention extension without exporting it in production files.

Risks/test signals: test-only API must remain aligned with the unexported helper signature. It has no direct assertions.
