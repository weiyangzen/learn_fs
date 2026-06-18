# sources/sync-backup/restic/internal/fs/sd_windows.go

Purpose: Windows security descriptor backup/restore helpers with high- and low-privilege modes.

Important APIs: `lowerPrivileges`, security flag sets, `getSecurityDescriptor`, `setSecurityDescriptor`, `getNamedSecurityInfoHigh/Low`, `setNamedSecurityInfoHigh/Low`, `isHandlePrivilegeNotHeldError`, `isAccessDeniedError`, `securityDescriptorBytesToStruct`, and `securityDescriptorStructToBytes`.

Control flow and state: A global atomic flag switches to lower privilege after `ERROR_PRIVILEGE_NOT_HELD`. Backup first tries full owner/group/DACL/SACL/security info, falls back to low privileges on access denied, and ignores unsupported filesystems. Restore parses SD bytes, extracts owner/group/DACL/SACL/control flags, applies high or low security info, and preserves DACL/SACL protection flags.

Dependencies and integration: Called by Windows generic attribute fill/restore in `node_windows.go`. Uses `x/sys/windows`, unsafe byte views, and restic errors.

Risks: Global `lowerPrivileges` affects subsequent operations process-wide. Low-privilege restore cannot restore owner/group/SACL fully. Unsafe byte-to-struct conversion requires valid self-relative SD bytes.

Test signals: `sd_windows_test.go`, `sd_windows_test_helpers.go`, and `node_windows_test.go` cover file/folder SD round-trips, admin vs non-admin expectations, and inheritance protection flags.
