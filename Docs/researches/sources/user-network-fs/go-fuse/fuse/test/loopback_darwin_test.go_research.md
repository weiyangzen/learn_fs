# `sources/user-network-fs/go-fuse/fuse/test/loopback_darwin_test.go`

## Purpose
Darwin-specific loopback integration tests.

## Important APIs, Types, And Functions
Covers macOS-only loopback expectations such as timestamp or filesystem semantics that differ from Linux.

## Control Flow
Covers macOS-only loopback expectations such as timestamp or filesystem semantics that differ from Linux.

## State And Persistence
State is temp backing/mount dirs. Risks are macFUSE version behavior and Darwin timestamp/xattr differences.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is temp backing/mount dirs. Risks are macFUSE version behavior and Darwin timestamp/xattr differences.

## Test Signals
State is temp backing/mount dirs. Risks are macFUSE version behavior and Darwin timestamp/xattr differences.
