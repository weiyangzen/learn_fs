# sources/sync-backup/restic/internal/fs/priv_windows_test.go

Purpose: Windows-only tests that privileges can bypass restrictive ACLs.

Important APIs: `TestBackupPrivilegeBypassACL`, `TestRestorePrivilegeBypassACL`, and `testGetRestrictedFilePath`.

Control flow and state: Tests skip without administrator membership. They create a file, deny read/write/execute to Everyone while allowing delete, then verify read open and write handle open with backup semantics.

Dependencies and integration: Exercises privilege enablement from package init and Windows security descriptor manipulation.

Risks: Requires admin rights and specific Windows ACL semantics. It does not directly assert which privilege was enabled, only resulting access behavior.

Test signals: Good integration signal that restic can access protected files for backup/restore on privileged Windows runs.
