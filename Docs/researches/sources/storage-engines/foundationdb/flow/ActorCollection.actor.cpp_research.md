# sources/storage-engines/foundationdb/flow/ActorCollection.actor.cpp

## Purpose
`ActorCollection.actor.cpp` implements the actor backing `ActorCollection`, a utility for dynamically adding `Future<Void>` actors, tracking their count, propagating errors, and optionally returning when the collection drains.

## Important APIs, Types, and Functions
`Runner` owns a handler future and is stored in a Boost intrusive `RunnerList`. `RunnerListDestroyer` guarantees list cleanup when the actor frame is destroyed. `runnerHandler` waits on one task and sends either its iterator to a completion stream or its error to an error stream. `actorCollection` is the main actor and is declared in the corresponding header. The file also defines `Traceable<std::pair<T, U>>` and `forceLinkActorCollectionTests`.

## Control Flow
`actorCollection` chooses among new actor arrivals, task completions, and task errors. New futures allocate a `Runner`, start a handler, and increment the external or internal count. Completion decrements the count, updates optional timing accumulators, optionally returns when empty, and erases the runner. Error events are thrown from the collection actor, causing the collection to become failed.

## State and Persistence Behavior
All state is in memory: the intrusive runner list, completion and error streams, count pointer, and optional activity timing pointers. There is no persistence. The destroyer is critical because actor cancellation must clear outstanding runner handlers and delete their allocations.

## Dependencies and Integration Points
The file depends on Flow actors, `ActorCollection.h`, `IndexedSet.h`, `UnitTest.h`, Boost intrusive lists, and the actor compiler. Workloads such as `WriteDuringRead` use `ActorCollection` to track concurrent commit futures.

## Risks and Edge Cases
The implementation relies on Flow `choose` behavior that promise fulfillment from one branch does not synchronously fire another branch in the same choose block. Reinitializing an `ActorCollection` is safer than just clearing it when the underlying add stream may contain queued futures.

## Test Signals
Unit tests cover choose behavior, cancellation of added actors on `clear`, and cancellation of actors queued in the promise stream after a failure and reinitialization.
