## sources/sync-backup/syncthing/lib/model/utils_test.go

Purpose: tests `inWritableDir` permission-tweaking behavior and Windows-specific filesystem workarounds around read-only directories and files.

Important tests: `TestInWriteableDir` checks callback execution inside a read-only fake directory and restoration of directory permissions. `TestOSWindowsRemove`, `TestOSWindowsRemoveAll`, and `TestInWritableDirWindowsRename` are Windows-only tests for removing or renaming read-only files/directories using fake/basic filesystems and the model helper.

Control flow and state: tests create temporary fake or basic filesystems, apply restrictive chmod modes, call `inWritableDir` or filesystem remove/rename operations, and assert final existence or contents.

Dependencies and integration points: relies on `build.IsWindows`, fake filesystem behavior, and `rand` path generation. It validates helper assumptions used by puller and osutil file operations.

Risks: platform-gated tests leave non-Windows behavior partly dependent on fake filesystem semantics. Permission behavior can differ by host filesystem mount options.

Test signals: targeted coverage for permission restoration and Windows read-only file handling.
