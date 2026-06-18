# `sources/user-network-fs/go-fuse/internal/testutil/verbose.go`

## Purpose
Shared verbose-test detection helper.

## Important APIs, Types, And Functions
`VerboseTest` checks the runtime stack for `TestNonVerbose` and reads `test.v`.

## Control Flow
`VerboseTest` checks the runtime stack for `TestNonVerbose` and reads `test.v`.

## State And Persistence
No persistence. Integrated into many mount options to enable debug logs under `go test -v`. Risk is stack-name heuristic and unavailable flag outside tests.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistence. Integrated into many mount options to enable debug logs under `go test -v`. Risk is stack-name heuristic and unavailable flag outside tests.

## Test Signals
No persistence. Integrated into many mount options to enable debug logs under `go test -v`. Risk is stack-name heuristic and unavailable flag outside tests.
