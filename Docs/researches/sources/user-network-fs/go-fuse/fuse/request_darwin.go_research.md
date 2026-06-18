# `sources/user-network-fs/go-fuse/fuse/request_darwin.go`

## Purpose
Darwin request layout specialization.

## Important APIs, Types, And Functions
Defines Darwin-specific request struct aliases/fields where macFUSE differs from generic Unix layouts.

## Control Flow
Defines Darwin-specific request struct aliases/fields where macFUSE differs from generic Unix layouts.

## State And Persistence
State is protocol layout only; risk is wire ABI mismatch with macFUSE. Integrated through shared `parseRequest` and platform build tags.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is protocol layout only; risk is wire ABI mismatch with macFUSE. Integrated through shared `parseRequest` and platform build tags.

## Test Signals
State is protocol layout only; risk is wire ABI mismatch with macFUSE. Integrated through shared `parseRequest` and platform build tags.
