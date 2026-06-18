# sources/test-tools/syzkaller/pkg/fuzzer/queue/prio_queue.go

## Purpose
This file provides a small generic heap wrapper used by dynamic ordering queues. Lower integer priority values are popped first.

## Important APIs, Types, And Functions
`priorityQueueOps[T]` wraps `priorityQueueImpl[T]` and exposes `Len`, `Push(item, prio)`, and `Pop`. `priorityQueueItem[T]` stores value and priority. `priorityQueueImpl[T]` implements `heap.Interface`: `Len`, `Less`, `Swap`, `Push`, and `Pop`.

## Control Flow
`Push` delegates to `heap.Push`; `Pop` returns the zero value when empty or heap-pops the next item. `Less` compares priorities ascending, making smaller priority values higher service priority.

## State And Persistence Behavior
State is an in-memory slice heap. `Pop` nils the removed slot to release references before shrinking the slice.

## Dependencies And Integration Points
It depends on the standard `container/heap` package and is used by `DynamicOrderer` in `queue.go` to order nested executor queues.

## Risks
Equal-priority ordering is not stable. Consumers that require FIFO ordering within a priority need a sequence tie-breaker, which this implementation does not provide.

## Test Signals
`prio_queue_test.go` confirms ascending priority order, zero value on empty pop, and zero length after all pops.
