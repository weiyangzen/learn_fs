# sources/sync-backup/restic/internal/fs/sd_windows_test.go

Purpose: Windows-only direct tests for security descriptor set/get.

Important APIs: `TestSetGetFileSecurityDescriptors`, `TestSetGetFolderSecurityDescriptors`, and `testSecurityDescriptors`.

Control flow and state: Creates temp file/folder targets, decodes base64 SD fixtures, sets each descriptor, gets it back, and delegates semantic comparison.

Dependencies and integration: Validates `setSecurityDescriptor`, `getSecurityDescriptor`, and helper comparison logic under current privilege level.

Risks: Base64 fixture semantics are opaque without helper decoding. Expected results differ for admin and non-admin users.

Test signals: Confirms SD byte restore/read behavior for both files and directories.
