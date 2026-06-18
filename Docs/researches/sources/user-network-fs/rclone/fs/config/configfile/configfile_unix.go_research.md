# sources/user-network-fs/rclone/fs/config/configfile/configfile_unix.go

Purpose: preserves group ownership when saving config files on Unix-like systems.

Important APIs/functions: `attemptCopyGroup(fromPath, toPath string)`.

Control flow: stats the existing config file, extracts `syscall.Stat_t`, starts with the old file's UID, prefers the current process user's UID when available, and calls `os.Chown` on the temp file with that UID and the old GID. Chown failures are logged at debug level.

State and persistence behavior: modifies ownership of the temporary config file before it is renamed into place. It does not alter file contents.

Dependencies and integration points: used by `Storage.Save` after creating the new temp file and before final rename. Depends on Unix build tags, `os/user`, `syscall`, and `fs.Debugf`.

Risks: user lookup or UID parsing may fail silently, falling back to the old UID. Chown can fail due to permissions; the save continues with a debug log.

Test signals: no direct unit test for group ownership in this subset; file mode behavior is tested on Linux in `configfile_test.go`.
