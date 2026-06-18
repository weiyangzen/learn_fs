# sources/user-network-fs/rclone/cmd/serve/nfs/nfs_unsupported.go

## Purpose

This fallback keeps the NFS package buildable on non-Unix platforms.

## Important APIs, Types, and Functions

It defines `var Command *cobra.Command` as nil.

## Control Flow

No NFS command is registered from this file.

## State and Persistence Behavior

No state is stored.

## Dependencies and Integration Points

The build tag is `!unix`. Callers must tolerate the command being unavailable.

## Risks and Test Signals

The risk is platform-specific command registration assumptions. Cross-platform build coverage is the main signal.
