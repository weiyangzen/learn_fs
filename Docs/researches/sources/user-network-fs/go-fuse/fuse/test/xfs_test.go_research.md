# `sources/user-network-fs/go-fuse/fuse/test/xfs_test.go`

## Purpose
Linux/XFS-oriented readdir-plus seek test.

## Important APIs, Types, And Functions
`TestReaddirPlusSeek` reuses loopback harness to validate directory seek offsets under READDIRPLUS-like behavior.

## Control Flow
`TestReaddirPlusSeek` reuses loopback harness to validate directory seek offsets under READDIRPLUS-like behavior.

## State And Persistence
State is temp directory entries and kernel directory offsets. Risk is filesystem-specific offset semantics; signal protects xfs-style cookies.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is temp directory entries and kernel directory offsets. Risk is filesystem-specific offset semantics; signal protects xfs-style cookies.

## Test Signals
State is temp directory entries and kernel directory offsets. Risk is filesystem-specific offset semantics; signal protects xfs-style cookies.
