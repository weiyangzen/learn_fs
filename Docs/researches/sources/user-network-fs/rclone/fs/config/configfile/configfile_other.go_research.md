# sources/user-network-fs/rclone/fs/config/configfile/configfile_other.go

Purpose: supplies a no-op `attemptCopyGroup` implementation for non-Unix platforms.

Important APIs/functions: `attemptCopyGroup(fromPath, toPath string)` is compiled when the OS is not in the Unix build tag set.

Control flow: no operation. It exists so `Storage.Save` can call the same helper cross-platform.

State and persistence behavior: does not alter file ownership or permissions.

Dependencies and integration points: complements `configfile_unix.go`. Used only during config save.

Risks: group ownership is not preserved on non-Unix platforms, which matches the stated platform model.

Test signals: no direct tests; platform-specific save tests are Linux-only in `configfile_test.go`.
