# sources/storage-engines/pebble/internal/intern/intern_test.go

## Purpose
`intern_test.go` verifies the allocation behavior expected from `intern.Bytes`.

## Important APIs, Types, And Functions
`TestBytes` constructs repeated `abc` byte slices, calls `Bytes` in a loop inside `testing.AllocsPerRun`, and fails if any allocations are observed. It skips when `buildtags.Race` is true.

## Control Flow
The test builds a repeated byte buffer and repeatedly interns 100 adjacent slices. The first warmup behavior of `AllocsPerRun` lets the pool/map become populated before allocation measurement.

## State And Persistence Behavior
The test relies on `sync.Pool` retaining a map during the run, but there is no persistent state. It explicitly avoids race builds because `sync.Pool` is effectively disabled there.

## Dependencies And Integration Points
It depends on `bytes`, `testing`, and Pebble `buildtags`. It directly measures the public `Bytes` helper.

## Risks And Edge Cases
Allocation counts are sensitive to compiler/runtime changes in string conversion and sync.Pool behavior. The test covers repeated equal short strings, not map growth or unique-string workloads.

## Test Signals
Passing outside race builds signals that repeated interning of known content is allocation-free in the intended runtime configuration.
