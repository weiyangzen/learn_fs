<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/sync/sync.go -->
# sources/user-network-fs/rclone/cmd/sync/sync.go

Source read: complete file, 108 lines, 4056 bytes, sha256 `3cf446b70a1c4ae2f04d8b160924b520d7c34ec41e9b577737c3f6aea52df9dd`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/sync/sync.go_research.md`.

## Purpose
Defines the high-risk `rclone sync` command, making destination contents match source and deleting destination-only data when appropriate.

## Important APIs, types, and functions
`createEmptySrcDirs`, logger options, and `commandDefinition` implement flags and command execution. Run parses source/destination with optional single source filename and calls `sync.Sync` or `operations.CopyFile`.

## Control flow
After argument validation, it configures optional loggers, attaches them to context if any logging flags are set, then delegates to sync operations for directory sync or file copy.

## State and persistence behavior
Persistent state is destination remote mutation: creates, updates, deletes, and optional empty source directory creation. Logger config can write external logs depending on flags.

## Dependencies and integration points
Depends on command framework, operations logger flags, `fs/sync`, and operations copy helpers.

## Risks and edge cases
This command can delete data; docs emphasize dry-run/interactive. Overlapping remotes, duplicate objects, filters, metadata root behavior, and delete-on-error safeguards are handled in delegated sync code but are critical risks.

## Test signals
Covered by broader sync/operations test suites outside this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/sync/sync.go -->
