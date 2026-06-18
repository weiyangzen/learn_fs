# `sources/user-network-fs/go-fuse/fuse/test/notify_linux_test.go`

## Purpose
Linux tests for inode notification invalidation.

## Important APIs, Types, And Functions
Defines `NotifyTest` harness and `TestInodeNotify`.

## Control Flow
Defines `NotifyTest` harness and `TestInodeNotify`.

## State And Persistence
State is backing content plus kernel cache/attrs. It validates that `InodeNotify` invalidates cached data/metadata. Risks are protocol-version and cache timing.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is backing content plus kernel cache/attrs. It validates that `InodeNotify` invalidates cached data/metadata. Risks are protocol-version and cache timing.

## Test Signals
State is backing content plus kernel cache/attrs. It validates that `InodeNotify` invalidates cached data/metadata. Risks are protocol-version and cache timing.
