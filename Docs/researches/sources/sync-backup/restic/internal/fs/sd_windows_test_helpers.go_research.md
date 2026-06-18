# sources/sync-backup/restic/internal/fs/sd_windows_test_helpers.go

Purpose: Shared Windows security descriptor fixtures and comparison helpers.

Important APIs: `testFileSDs`, `testDirSDs`, `isAdmin`, and `compareSecurityDescriptors`.

Control flow and state: `isAdmin` checks membership in the built-in Administrators SID. `compareSecurityDescriptors` parses input/output SDs and compares owner, group, DACL, and SACL expectations, adjusting owner/group/SACL expectations for non-admin restores.

Dependencies and integration: Used by SD and Windows node tests to avoid byte-for-byte comparisons that would be wrong under low privilege.

Risks: Assumes current user SID/group SID are available through `os/user`. Comparison depends on Windows APIs for SID equality and ACL equality.

Test signals: Provides the semantic oracle for security descriptor round-trip tests.
