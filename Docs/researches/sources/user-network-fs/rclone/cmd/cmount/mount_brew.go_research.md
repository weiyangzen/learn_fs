<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount_brew.go -->
# sources/user-network-fs/rclone/cmd/cmount/mount_brew.go

## Purpose

This macOS Homebrew build-tag variant registers `rclone mount` but returns a clear unsupported error because Homebrew builds lack the required FUSE support.

## Important APIs, Types, and Functions

`init` registers a mount command and `cmount` alias through `mountlib`, plus the rc mount hook. The local `mount` function matches the mountlib signature and always returns an explanatory error.

## Control Flow

Any attempt to mount reaches the stub and fails before creating VFS or cgofuse state.

## State and Persistence Behavior

No mount, remote mutation, or local persistent state is created.

## Dependencies and Integration Points

It integrates with macOS `brew` build tags, `mountlib`, and VFS only for type compatibility.

## Risks and Test Signals

Risks are misleading command availability or stale installation guidance. Build-tag tests should verify this variant compiles, registers expected aliases, and returns the exact unsupported path instead of attempting a mount.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount_brew.go -->
