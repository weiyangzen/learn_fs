# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/CallQueueManager.java

## Purpose
Wraps an IPC server call queue and scheduler, adding priority scheduling, optional client backoff, and queue-overflow exceptions.

## Important APIs, Types, And Functions
`CallQueueManager<E extends Schedulable>` extends `AbstractQueue` and implements `BlockingQueue`. Key methods create scheduler/queue instances reflectively, `put`, `add`, `offer`, `take`, `poll`, `peek`, `remainingCapacity`, `drainTo`, scheduler helpers, and nested `CallQueueOverflowException`.

## Control Flow
Construction reads priority levels, builds scheduler and queue via preferred constructors. `put()` blocks unless backoff is enabled; with backoff it checks `scheduler.shouldBackOff`. `add()` maps queue-full or scheduler backoff to `CallQueueOverflowException.DISCONNECT`. Consumers read from `takeRef`; producers write through `putRef`.

## State And Persistence
State is active backing queue references, scheduler, and volatile backoff flag. No persistence. Atomic references are structured for queue swapping, though this file does not expose a swap method.

## Dependencies And Integration Points
Integrates server `Schedulable`, `RpcScheduler`, `DecayRpcScheduler`, `FairCallQueue`, `ProcessingDetails`, Hadoop `Configuration`, UGI, and IPC protobuf status codes.

## Risks
Reflection constructor matching can fail at runtime for custom queues/schedulers. `putRef`/`takeRef` can diverge in future swap logic, so methods intentionally choose one side. `take()` polls every second, so shutdown/empty waits are not immediate. Backoff always uses `DISCONNECT` here.

## Test Signals
Useful tests cover constructor fallback order, priority-level config parsing, queue-full behavior, backoff decisions, custom overflow exceptions, scheduler metric hooks, and blocking `take()` interruption.
