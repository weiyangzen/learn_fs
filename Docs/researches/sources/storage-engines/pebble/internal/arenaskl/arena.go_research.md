<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/arena.go -->
# sources/storage-engines/pebble/internal/arenaskl/arena.go

## Purpose
This file implements the lock-free byte arena backing Pebble's concurrent arena skiplist.

## Important APIs, Types, And Functions
`Arena` holds an atomic allocation offset and backing buffer. `NewArena` reserves offset zero as nil. `Size`, `Capacity`, `alloc`, `getBytes`, `getPointer`, and `getPointerOffset` provide allocation and offset/pointer conversion. `ErrArenaFull`, `MaxArenaSize`, and `nodeAlignment` define limits.

## Control Flow
Allocation validates alignment under invariants, checks prior overflow, atomically adds padded size, verifies capacity plus overflow allowance, and returns an aligned offset.

## State And Persistence Behavior
All state is process-local. Failed allocation may push the internal counter beyond capacity; `Size` saturates to `MaxArenaSize`.

## Dependencies And Integration Points
It depends on `sync/atomic`, `unsafe`, `invariants`, and errors. `node.go` and `skl.go` allocate skiplist nodes from it.

## Risks And Edge Cases
Pointer arithmetic and offset truncation are load-bearing. Oversized buffers are truncated or panic under invariants. `alloc` requires power-of-two alignment and reserves overflow bytes for truncated node towers.

## Test Signals
`arena_test.go` checks overflow saturation, and `race_test.go` checks node allocation at arena boundaries under the race detector.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/arena.go -->
