<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/touch/touch.go -->
# sources/user-network-fs/rclone/cmd/touch/touch.go

## Purpose

`touch.go` implements `rclone touch`, creating empty objects or updating modification times for files and directory contents on any rclone backend.

## Important APIs, Types, and Functions

Global flags are `notCreateNewFile`, `timeAsArgument`, `localTime`, and `recursive`. Helpers include `newFsDst`, `parseTimeArgument`, `timeOfTouch`, and `createEmptyObject`. The main API is `Touch(ctx, f, remote) error`, which is directly testable apart from Cobra.

## Control Flow

The command splits the destination path into a parent fs and basename. `Touch` chooses a timestamp, probes `f.NewObject`, handles missing objects by optionally creating an empty object, handles directories via `operations.TouchDir` with recursive or shallow mode, and updates existing files with `SetModTime` after dry-run/interactive destructive checks.

## State and Persistence Behavior

The command mutates remote object modtimes and may create zero-byte objects with metadata-derived open options. Global flag variables persist across tests/commands in process. Recursive mode deliberately never creates missing files.

## Dependencies and Integration Points

It integrates with `cmd.Run`, `fspath.Split`, backend `Put`/`NewObject`/`SetModTime`, `object.NewStaticObjectInfo`, metadata flags, and operations destructive-skip logic.

## Risks and Test Signals

Risks include global flag leakage between tests, timestamp layout ambiguity by string length, timezone surprises with `--localtime`, backend precision differences, and directory/nonexistent path behavior. Tests should cover creation, no-create, timestamp formats, recursive directories, empty remotes, dry-run, metadata creation, and unsupported modtime backends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/touch/touch.go -->
