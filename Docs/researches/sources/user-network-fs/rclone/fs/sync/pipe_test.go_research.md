# sources/user-network-fs/rclone/fs/sync/pipe_test.go

## Purpose
This file tests the sync pipeline queue implementation.

## Important APIs, Types, and Functions
- Interface assertion verifies `pipe` satisfies `heap.Interface`.
- `TestPipe` checks stats, delete-signal size accounting, close/read behavior, write-after-close panic, and cancellation.
- `TestPipeConcurrent` stresses concurrent put/get pairs.
- `TestPipeOrderBy` checks queue ordering for name, size, modtime, ascending, descending, and mixed modes.
- `TestNewLess` validates parsing errors and comparator behavior.

## Control Flow
Tests create mock objects with content, enqueue object pairs, read them back, and assert queue stats and object order. Concurrent tests run paired reader/writer goroutines and use an atomic counter to verify balance.

## State and Persistence
All state is in memory and uses mock objects. No filesystem persistence is touched.

## Dependencies and Integration Points
It uses `mockobject`, `fs.ObjectPair`, `container/heap`, `sync`, `atomic`, and `testify`. It protects the behavior consumed by the high-concurrency sync engine in `sync.go`.

## Risks and Edge Cases
Concurrent assertions inside goroutines can produce multiple failures but are still useful for race detection when run with `-race`. Modtime comparator tests use mock object defaults, so they mainly protect parser/comparator wiring rather than backend-specific modtime costs.

## Test Signals
The tests give good evidence for queue correctness, stats callbacks, cancellation, and order parsing. They should be paired with race testing for stronger concurrency confidence.
