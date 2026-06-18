# sources/storage-engines/badger/y/watermark.go

## Purpose
This file implements `WaterMark`, a concurrent tracker for the highest contiguous completed index. It is used by Badger/related systems to coordinate asynchronous work completion and waiters.

## Important APIs, Types, And Functions
`uint64Heap` is a min-heap of pending indices. `mark` represents begin/done events, batched indices, or waiters. `WaterMark` exposes `Init`, `Begin`, `BeginMany`, `Done`, `DoneMany`, `DoneUntil`, `SetDoneUntil`, `LastIndex`, and `WaitForMark`. The background `process` goroutine owns mutable maps.

## Control Flow
`Begin` and `Done` send events to `markCh`; processing increments or decrements a pending count per index, pushes first-seen indices onto the heap, and advances `doneUntil` while the minimum pending index has non-positive count. Waiters are closed when their requested index is already or newly covered.

## State And Persistence Behavior
State is in-memory: atomic `doneUntil`, atomic `lastIndex`, buffered channel, pending counts, heap, and waiter map. `SetDoneUntil` directly updates the atomic baseline and must not be intermingled incorrectly with begin/done events.

## Dependencies And Integration Points
It depends on `container/heap`, `context`, atomics, and `z.Closer`. Transaction/oracle code relies on watermark advancement for timestamp and conflict lifecycle.

## Risks And Edge Cases
The comments require each serial index to emit at least one begin watermark or waiters can block indefinitely. `processOne` fatals if an event arrives below `doneUntil`. Notification logic avoids huge loops when index arithmetic wraps or spans a very large range.

## Test Signals
`watermark_edge_test.go` indirectly stresses transaction watermark behavior. Direct unit tests are not in this subset.
