# sources/storage-engines/foundationdb/flow/IThreadPoolTest.cpp

## Purpose
Provides Linux-only unit tests for the generic Flow thread pool, thread naming, thread-safe promise streams, and pool shutdown ownership.

## Important APIs, Types, And Functions
`ThreadNameReceiver` handles `GetNameAction` and returns `pthread_getname_np()`. `getThreadName()` and `waitForThreadName()` post and poll name actions. `ThreadSafePromiseStreamSender` sends thread names or injected fault errors through `ThreadReturnPromiseStream`. `MockReceiver`, `MockTask`, and `initTestPool()` support shutdown tests. `forceLinkIThreadPoolTests()` ensures registration/linkage.

## Control Flow
Tests create a generic pool, add a named worker, post actions, await futures/streams, tolerate delayed name propagation, validate expected names when available, verify injected fault propagation, and stop or drop the pool to exercise both explicit and implicit cleanup.

## State And Persistence Behavior
Uses transient pools, worker threads, promises, and futures. No file/network persistence.

## Dependencies And Integration Points
Depends on Linux pthread naming, Flow coroutines, `IThreadPool`, `UnitTest`, `g_network` task priority management, `ThreadReturnPromise`, and injected-fault `Error` flags.

## Risks And Edge Cases
Thread naming is Linux-only and can be delayed after `pthread_create()`, so tests poll up to 5 seconds and tolerate environments where the name is unavailable in the stream test. Non-Linux builds compile only a force-link stub. Promise validity assertions catch double-send behavior.

## Test Signals
Registers `/flow/IThreadPool/NamedThread`, `/flow/IThreadPool/ThreadReturnPromiseStream`, `/flow/IThreadPool/ExplicitStop`, and `/flow/IThreadPool/ImplicitStop`.
