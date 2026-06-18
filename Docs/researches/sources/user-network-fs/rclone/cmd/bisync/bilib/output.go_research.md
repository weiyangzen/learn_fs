# sources/user-network-fs/rclone/cmd/bisync/bilib/output.go

Purpose: test/helper utility to capture rclone log output emitted during a function call. `CaptureOutput` temporarily sets log level to INFO and replaces the log handler output callback with a buffer writer guarded by a mutex.

State changes are global log handler level/output mutation, restored with defer. Dependencies are rclone `fs/log`, `log/slog`, bytes, and sync. Risks include global logging interference in concurrent tests, missed lower-level output because level is forced to INFO, and capture scope depending on defer restoration after panics. Test signal is indirect: consumers can assert log output deterministically.
