<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mountpoint_other.go -->
# sources/user-network-fs/rclone/cmd/cmount/mountpoint_other.go

## Purpose

`mountpoint_other.go` validates non-Windows cmount mountpoints.

## Important APIs, Types, and Functions

`getMountpoint(f fs.Fs, mountPath string, opt *mountlib.Options)` stats the mount path, requires an existing directory, checks source/mount overlap with `mountlib.CheckOverlap`, checks non-empty policy with `mountlib.CheckAllowNonEmpty`, and returns the path.

## Control Flow

Validation is sequential and returns the first error. No mount is attempted here.

## State and Persistence Behavior

The function is read-only against the local filesystem and remote Fs metadata. It does not create directories.

## Dependencies and Integration Points

It is selected for `cmount && cgo && !windows` builds and is called by `mount.go`.

## Risks and Test Signals

Risks include rejecting useful paths because they do not exist, overlap false positives, and platform-specific non-empty semantics. Tests should cover nonexistent path, file path, empty directory, non-empty directory with/without allow flag, and local remote overlap.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mountpoint_other.go -->
