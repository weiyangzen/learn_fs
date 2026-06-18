<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/race_test.go -->
# sources/storage-engines/pebble/internal/arenaskl/race_test.go

## Purpose
This race-build-only test validates node allocation at the end of small arenas, targeting pointer alignment issues detected by Go's race detector.

## Important APIs, Types, And Functions
`TestNodeArenaEnd` repeatedly calls `newArena` and `newNode` with increasing arena sizes.

## Control Flow
The loop expects `ErrArenaFull` until the arena is large enough. Once allocation succeeds, the test stops; race detector instrumentation would report boundary/alignment problems during the attempts.

## State And Persistence Behavior
Only transient arena memory is involved.

## Dependencies And Integration Points
It is guarded by `//go:build race`, uses `testify/require`, and depends on helper constructors from `skl_test.go`.

## Risks And Edge Cases
The targeted risk is a node's truncated tower or overflow reservation straddling the arena boundary in a way unsafe instrumentation observes as invalid memory.

## Test Signals
It provides specialized race-detector coverage not exercised in normal builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/race_test.go -->
