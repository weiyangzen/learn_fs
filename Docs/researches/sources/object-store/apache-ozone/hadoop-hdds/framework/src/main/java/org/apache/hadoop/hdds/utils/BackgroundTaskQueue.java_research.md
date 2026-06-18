# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundTaskQueue.java

Purpose: `BackgroundTaskQueue` is a synchronized priority queue for `BackgroundTask` instances used by `BackgroundService`.

Important APIs/types/functions: constructor creates a `PriorityQueue` ordered by `BackgroundTask.getPriority()`. `add()`, `poll()`, `isEmpty()`, and `size()` are synchronized.

Control flow: service subclasses fill the queue in `getTasks()`. `BackgroundService.PeriodicalTask` polls until empty and submits each task for asynchronous execution.

State and persistence: in-memory priority queue only.

Dependencies/integration: depends on `BackgroundTask`; used by framework unit tests and component background services.

Risks: synchronization protects individual queue operations, but callers that check `isEmpty()` then `poll()` depend on external single-consumer behavior. Equal-priority ordering is not stable because `PriorityQueue` does not preserve insertion order.

Test signals: `TestBackgroundService` and disk balancer tests call/get task queues; background service behavior validates priority queue consumption.
