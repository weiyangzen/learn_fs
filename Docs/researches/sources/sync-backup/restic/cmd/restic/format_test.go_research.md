# sources/sync-backup/restic/cmd/restic/format_test.go

Purpose: unit tests for `formatNode`.

Important APIs/types/functions: `TestFormatNode`.

Control flow and state: temporarily forces `time.Local` to UTC, constructs a file node, and checks output for non-long path-only mode, long raw-size mode, and long human-readable mode.

Dependencies and integration points: uses `data.Node`, time formatting, and restic test equality.

Risks: only regular file formatting is covered; symlinks, dirs, devices, fifos, and sockets are not tested here.

Test signals: protects the basic text `ls -l` output shape and stable timestamp formatting under UTC.
