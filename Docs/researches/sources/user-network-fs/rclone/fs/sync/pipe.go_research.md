# sources/user-network-fs/rclone/fs/sync/pipe.go

## Purpose
This file implements an internal unbounded object-pair queue for sync/copy/move pipelines, with optional heap ordering and queue-size accounting.

## Important APIs, Types, and Functions
- `pipe` stores a mutex-protected queue, a signaling channel, total queued size, stats callback, ordering comparator, and mixed-order fraction.
- `newPipe(orderBy, stats, maxBacklog)` constructs the pipe and parses ordering.
- `Put`, `Get`, `GetMax`, `Stats`, and `Close` provide queue operations.
- Heap methods `Len`, `Less`, `Swap`, `Push`, and `Pop` support ordered queues through `deheap`.
- `newLess(orderBy)` parses order strings by name/size/modtime and ascending/descending/mixed direction.

## Control Flow
`Put` locks, appends or heap-pushes, updates total size for non-delete pairs, calls stats, unlocks, then sends a token to the buffered channel. `GetMax` waits for a token, locks, pops FIFO or heap min/max depending on order and fraction, updates stats, and returns the pair. `Close` closes the signaling channel; subsequent writes panic via send on closed channel semantics.

## State and Persistence
State is in-memory only. The queue holds `fs.ObjectPair` references and deliberately clears removed entries to avoid retaining objects. `totalSize` tracks queued source sizes excluding `Src == Dst` delete signals.

## Dependencies and Integration Points
It depends on `fs.ObjectPair`, `fserrors.FatalError`, `math/bits`, and `github.com/aalpar/deheap`. `sync.go` uses pipes for checker, transfer, and rename queues, feeding accounting queue stats callbacks.

## Risks and Edge Cases
The pipe is not strictly ordered without `--order-by`; it approximates unbounded channel behavior with separate queue and token channel. `maxBacklog < 0` uses the largest positive int, which can allocate a very large buffered channel. Modtime ordering calls `ModTime(context.Background())`, which may be expensive or unsupported. `Close` is not idempotent and write-after-close panics by design.

## Test Signals
`pipe_test.go` covers basic put/get/close/cancel behavior, concurrent producers/consumers, order-by variants, mixed fractions, and invalid order strings.
