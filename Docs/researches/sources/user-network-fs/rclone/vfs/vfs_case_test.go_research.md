<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfs_case_test.go -->
# sources/user-network-fs/rclone/vfs/vfs_case_test.go

## Purpose
Tests VFS path lookup behavior for case-insensitive mode and Unicode normalization.

## Important APIs, Types, and Functions
Main tests are `TestCaseSensitivity` and `TestUnicodeNormalization`; helpers are `checkFileDataVFS`, `assertFileDataVFS`, and `assertFileAbsentVFS`.

## Control Flow
Case testing creates remote files whose names differ by case, builds case-sensitive and case-insensitive VFS instances, verifies normal lookup, detects whether the backend truly preserves case-sensitive distinct objects, then tests folded lookup and ambiguous folded names. Unicode testing creates NFC and plain-name files, reads them through NFD names, then toggles global `NoUnicodeNormalization` and verifies normalized lookup behavior changes.

## State and Persistence Behavior
Tests persist remote objects through `fstest.Run`; VFS instances maintain their own directory caches. The Unicode test temporarily mutates global config `NoUnicodeNormalization` and restores it with `defer`.

## Dependencies and Integration Points
Uses `fstest`, `vfscommon.Options.CaseInsensitive`, global `fs.GetConfig`, and `golang.org/x/text/unicode/norm`. It depends on `Dir` lookup behavior not present in this subset but validates it through `VFS.OpenFile`.

## Risks and Edge Cases
Case tests skip when backend cannot provide meaningful case-sensitive behavior. Ambiguous case-insensitive lookups only assert an error other than `ENOENT`, not a specific error. Global config mutation can affect parallel tests if not isolated.

## Test Signals
Strong signal for lookup normalization behavior and ambiguous case-folded names. It validates user-visible path compatibility across remotes with different case and Unicode semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfs_case_test.go -->
