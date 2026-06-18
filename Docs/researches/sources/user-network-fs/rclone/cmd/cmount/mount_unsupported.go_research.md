<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount_unsupported.go -->
# sources/user-network-fs/rclone/cmd/cmount/mount_unsupported.go

## Purpose

This fallback file keeps the `cmount` package buildable when cmount support is not selected or not supported.

## Important APIs, Types, and Functions

It declares only `package cmount`; there are no functions, commands, or state.

## Control Flow

No runtime code executes. Unsupported builds rely on other mount implementations or omit cmount command registration.

## State and Persistence Behavior

No state or persistence behavior exists.

## Dependencies and Integration Points

The build expression excludes supported cgo cmount platforms and Windows cmount builds. Its integration point is the Go package loader.

## Risks and Test Signals

Risk is a build-tag gap that leaves no buildable source. Matrix builds should confirm unsupported targets compile and supported targets do not accidentally pick this placeholder.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount_unsupported.go -->
