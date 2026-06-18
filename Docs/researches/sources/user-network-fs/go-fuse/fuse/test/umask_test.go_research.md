# `sources/user-network-fs/go-fuse/fuse/test/umask_test.go`

## Purpose
Tests create/mkdir umask propagation through pathfs/nodefs.

## Important APIs, Types, And Functions
`TestUmask` mounts loopback variants and creates files/directories under known umask expectations.

## Control Flow
`TestUmask` mounts loopback variants and creates files/directories under known umask expectations.

## State And Persistence
State is temp backing/mount dirs and process umask. Signal protects mode calculation from kernel to filesystem. Risk is process-global umask interference.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is temp backing/mount dirs and process umask. Signal protects mode calculation from kernel to filesystem. Risk is process-global umask interference.

## Test Signals
State is temp backing/mount dirs and process umask. Signal protects mode calculation from kernel to filesystem. Risk is process-global umask interference.
