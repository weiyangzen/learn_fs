# sources/sync-backup/restic/cmd/restic/integration_helpers_windows_test.go

Purpose: Windows-specific implementations for integration directory comparison and hardlink grouping.

Important APIs/types/functions: `(*dirEntry).equals`; `nlink`; `inode`; `createFileSetPerHardlink`.

Control flow and state: equality checks path, mode, and modification time only. `nlink` returns 1, `inode` returns 0, and hardlink grouping assigns synthetic IDs by directory entry index.

Dependencies and integration points: complements the Unix helper file under the `windows` build tag and supports shared tests without relying on Unix stat fields.

Risks: synthetic inode/link behavior means Windows tests cannot validate hardlink identity the same way Unix tests can. Fewer metadata fields are compared.

Test signals: indirectly exercised by cross-platform integration tests that compare restored directory contents.
