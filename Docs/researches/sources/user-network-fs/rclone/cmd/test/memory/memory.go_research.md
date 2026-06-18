<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/memory/memory.go -->
# sources/user-network-fs/rclone/cmd/test/memory/memory.go

## Purpose

`memory.go` implements `rclone test memory`, a diagnostic command that lists all objects under a remote, retains them in memory, optionally reads metadata, and reports allocation/system-memory deltas per object.

## Important APIs, Types, and Functions

The file exposes only its Cobra `commandDefinition`. The run function uses `operations.Count`, `operations.ListFn`, `runtime.GC`, `runtime.ReadMemStats`, and `fs.GetMetadata`. Formatting depends on `ConfigInfo.HumanReadable` and feature detection through `fsrc.Features().ReadMetadata`.

## Control Flow

The command validates one source remote, counts objects to size the slice, snapshots memory after a GC, lists objects into a mutex-protected slice, optionally fetching metadata to include cached metadata cost, then snapshots memory again and logs object count, allocation delta, bytes/object, and Go runtime `Sys` delta.

## State and Persistence Behavior

The command stores listed `fs.Object` instances only for the process lifetime. It does not mutate the remote, but it can warm backend metadata caches and use significant heap on large remotes. Global config is read, not modified.

## Dependencies and Integration Points

It lives under `rclone test`, uses the standard command runner, and integrates with backend listing, metadata feature flags, rclone logging, and Go runtime memory statistics.

## Risks and Test Signals

Risks include divide-by-zero when a remote has zero objects, high memory use on very large remotes, concurrent callback ordering, and backend-specific metadata side effects. Tests should cover empty remotes, metadata-supported and unsupported backends, human and raw formatting, count/list errors, and large-count capacity behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/memory/memory.go -->
