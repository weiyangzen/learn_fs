<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/arena_test.go -->
# sources/storage-engines/pebble/internal/arenaskl/arena_test.go

## Purpose
This file tests arena allocation accounting around maximum sizes and overflow.

## Important APIs, Types, And Functions
`newArena` wraps `NewArena`. `TestArenaSizeOverflow` calls `alloc`, `Size`, and compares errors with `ErrArenaFull`.

## Control Flow
The test allocates under the limit, then attempts a `math.MaxUint32` allocation that would overflow with 32-bit arithmetic, then verifies subsequent allocations continue failing.

## State And Persistence Behavior
It checks only in-memory arena offset state and saturation of `Size`.

## Dependencies And Integration Points
It uses `math`, `testing`, and `testify/require`.

## Risks And Edge Cases
The key regression risk is offset accounting wrapping around after a failed oversized allocation. The test expects `Size` to saturate to `MaxArenaSize`.

## Test Signals
Direct assertions cover success under the limit, `ErrArenaFull` over the limit, and stable full-state behavior afterward.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/arena_test.go -->
