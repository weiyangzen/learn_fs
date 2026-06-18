<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/settier/settier.go -->
# sources/user-network-fs/rclone/cmd/settier/settier.go

Source read: complete file, 64 lines, 1827 bytes, sha256 `2a53951c8d05f1b0d45c633419a287dffe95b1eae90b9adbc9c631bdb64d6fe3`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/settier/settier.go_research.md`.

## Purpose
Defines the `rclone settier` command for changing storage class or tier on all objects under a remote path.

## Important APIs, types, and functions
`commandDefinition` is a Cobra command registered in init. Its Run function parses `tier` and `remote:path`, constructs an Fs, checks `Features().SetTier`, and calls `operations.SetTier`.

## Control flow
Execution is straightforward: validate two args, build source Fs, enter `cmd.Run`, reject unsupported backends, then delegate recursive tier mutation to operations.

## State and persistence behavior
Persistent state is remote object storage tier/class changed by the backend. No local state is stored.

## Dependencies and integration points
Depends on rclone command framework, Fs feature flags, and operations tiering.

## Risks and edge cases
Tier changes can make objects unavailable or incur provider costs; command only checks feature presence, not provider-specific tier validity before delegation.

## Test signals
Covered by operation/backend tests rather than a local test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/settier/settier.go -->
