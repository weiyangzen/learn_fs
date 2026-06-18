# sources/storage-engines/wiredtiger/test/cppsuite/src/util/barrier.h

## Purpose
Declares a simple reusable synchronization barrier for multiple worker threads.

## Important APIs, Types, And Functions
`barrier` deletes copy/assignment, provides `barrier(std::size_t thread_count)`, `wait`, and default destructor. Private fields include mutex, condition variable, threshold, current count, generation, and a 600-second timeout.

## Control Flow
Callers construct it with the number of participating threads and each calls `wait` at synchronization points.

## State And Persistence Behavior
Only transient synchronization state is stored. There is no filesystem or WiredTiger persistence.

## Dependencies And Integration Points
Includes condition variable and mutex headers. Integrated through `thread_worker` optional shared barrier pointer.

## Risks And Test Signals
All expected participants must call `wait`; otherwise waiters time out. Because the barrier is reusable, callers must avoid destroying it while workers can still call it.
