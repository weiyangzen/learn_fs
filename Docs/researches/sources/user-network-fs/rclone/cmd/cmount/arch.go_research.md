<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/arch.go -->
# sources/user-network-fs/rclone/cmd/cmount/arch.go

## Purpose

`arch.go` reports whether cgo-FUSE support is provided for a target OS.

## Important APIs, Types, and Functions

`ProvidedBy(osName string) bool` returns true for `windows` and `darwin`, false otherwise.

## Control Flow

There is no complex flow; callers pass an OS name and receive a capability answer.

## State and Persistence Behavior

The function is stateless and has no persistence behavior.

## Dependencies and Integration Points

It integrates with build/support reporting that needs to distinguish cmount-capable platform binaries.

## Risks and Test Signals

Risk is divergence from actual build tags and platform support. Tests should compare `ProvidedBy` with the maintained cmount support matrix for linux, darwin, windows, BSDs, and unsupported OS names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/arch.go -->
