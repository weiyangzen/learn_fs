# sources/sync-backup/restic/internal/fs/priv_windows.go

Purpose: Enables Windows backup/restore/security/take-ownership privileges for the process.

Important APIs: `processPrivileges` and `enableProcessPrivileges`.

Control flow and state: Iterates privileges one at a time using `winio.EnableProcessPrivileges`, joins errors, and returns aggregate failure information. Enabling one at a time avoids misleading all-or-nothing errors.

Dependencies and integration: Called at package init before local filesystem operations. Supports ACL bypass, security descriptor access, and restore of protected metadata.

Risks: Privilege availability depends on admin/token rights. Errors are logged by init rather than fatal, so later operations may fall back or fail with lower privilege.

Test signals: `priv_windows_test.go` checks backup/restore privilege behavior on restricted ACLs when running as admin.
