# sources/test-tools/syzkaller/pkg/fuzzer/queue/queue.go

## Purpose
This file defines the fuzzer execution queue abstraction and a set of composable queue/source wrappers. It is the boundary between request producers and executor consumers.

## Important APIs, Types, And Functions
`Request` describes executable work: request type, exec options, program or binary/glob data, signal/output/error return options, completion stat, importance, executor avoidance, completion callback chain, retry state, and wait channel. `ExecutorID` identifies VM/proc. `DoneCallback` can intercept completion. `Result` carries `ProgInfo`, executor ID, output, status, and error. `Status` distinguishes success, executor failure, crash, restart, and hang.

Core methods include `Request.OnDone`, `Done`, `Wait`, `Risky`, `Validate`, `hash`, and `initChannel`; `Result.clone`, `Stop`, and `GlobFiles`; and queue interfaces `Executor` and `Source`.

Queue implementations and wrappers include `PlainQueue` FIFO, `Order`, `Callback`, `Alternate`, `DynamicOrderer`, `DynamicSourceCtl`, `Deduplicate`, `DefaultOpts`, `RandomQueue`, and `Tee`.

## Control Flow
Producers call `Submit`; consumers call `Next`; executors eventually call `Done`. `OnDone` composes callbacks in LIFO order, and any callback can stop further processing by returning false. `Wait` blocks on request completion or context cancellation. `Deduplicator.Next` hashes requests, runs the first unique request, queues duplicate waiters until the result is known, then broadcasts cloned results. `DefaultOpts` ORs default flags into each request. `RandomQueue` randomly evicts or returns entries. `Tee` duplicates a minimal copy of each request to another executor while returning the original.

## State And Persistence Behavior
State is in-memory and concurrency-protected with mutexes/atomics. Requests carry mutable callback, result, done channel, crash/retry markers, and delayed sequence. `PlainQueue` compacts its slice after enough consumed entries. `Deduplicator` caches all seen request hashes and results for the life of the wrapper. `RandomQueue` can complete evicted requests with `ExecFailure`.

## Dependencies And Integration Points
It depends on `flatrpc` for request types and exec flags, `prog` for program serialization/cloning, `hash`, `stat`, `encoding/gob`, and standard concurrency packages. The fuzzer uses `Plain`, `DynamicOrder`, `Order`, and callbacks heavily; retry/distributor wrappers can sit between fuzzer and RPC executor.

## Risks
`Request.OnDone` mutates the callback chain without locking and is intended to be configured before concurrent completion. `Deduplicator` may grow without eviction and hashes serialized programs/options rather than all request sideband fields. `Request.Validate` requires a sandbox for program requests, so callers must apply defaults before validation. `Tee` only copies core execution identity fields and intentionally drops return flags/importance/callbacks.

## Test Signals
`queue_test.go` covers FIFO behavior, dynamic priority ordering, glob output parsing, and tee copy semantics. Retry and priority primitives have separate tests.
