# `sources/user-network-fs/go-fuse/internal/testutil/log.go`

## Purpose
Test logging initialization.

## Important APIs, Types, And Functions
`init` sets standard log flags to microseconds for tests.

## Control Flow
`init` sets standard log flags to microseconds for tests.

## State And Persistence
Global process log state is modified. Risk is test-global side effect, but it improves timing diagnostics.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Global process log state is modified. Risk is test-global side effect, but it improves timing diagnostics.

## Test Signals
Global process log state is modified. Risk is test-global side effect, but it improves timing diagnostics.
