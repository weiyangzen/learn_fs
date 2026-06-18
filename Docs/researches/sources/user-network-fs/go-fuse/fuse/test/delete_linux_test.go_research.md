# `sources/user-network-fs/go-fuse/fuse/test/delete_linux_test.go`

## Purpose
Linux test for delete notifications.

## Important APIs, Types, And Functions
`TestDeleteNotify` mounts a filesystem, removes/renames entries, and checks kernel-visible delete notification behavior.

## Control Flow
`TestDeleteNotify` mounts a filesystem, removes/renames entries, and checks kernel-visible delete notification behavior.

## State And Persistence
State lives in temp mount and kernel dentry cache. Risk is Linux-only notification support and timing around cached directory entries.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State lives in temp mount and kernel dentry cache. Risk is Linux-only notification support and timing around cached directory entries.

## Test Signals
State lives in temp mount and kernel dentry cache. Risk is Linux-only notification support and timing around cached directory entries.
