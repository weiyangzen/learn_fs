# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/BackgroundService.java

Purpose: `BackgroundService` is an abstract scheduler for periodic Ozone background work. Each interval obtains a `BackgroundTaskQueue`, runs tasks concurrently on a scheduled pool, waits for prior tasks before starting the next batch, and logs slow tasks.

Important APIs/types/functions: constructors configure service name, interval/unit, pool size, timeout, and optional thread prefix. `start()` schedules the `PeriodicalTask` with fixed delay. `shutdown()` stops the executor safely. `setPoolSize()`, `setServiceTimeoutInNanos()`, `setInterval()`, and `getIntervalMillis()` adjust runtime behavior. Subclasses implement `getTasks()` and may override `execTaskCompletion()`. Test helpers expose executor/thread count and `runPeriodicalTaskNow()`.

Control flow: each `PeriodicalTask.run()` joins the previous `future`, calls completion hook, gets tasks, and chains each task into `future` via `CompletableFuture.runAsync(..., exec).exceptionally(...)` combined with prior future. Each task call logs result size, catches `Throwable`, rethrows `Error`, and warns if elapsed nanos exceed timeout.

State and persistence: state includes scheduled executor, thread group, service interval, timeout, pool size, service task, and current completion future. No durable persistence.

Dependencies/integration: used by block deletion, disk balancer, snapshot maintenance, and other periodic services. Depends on Guava thread factories, Ratis `TimeDuration`, Java concurrency, and local background task/result queues.

Risks: tasks run on the same scheduled executor used to schedule periods, so pool sizing affects both scheduling and work. The future chain can grow over many intervals if not reset, though completed futures are lightweight. `ThreadGroup.destroy()` is deprecated and only attempted when active count is zero. Shutdown must not be called while holding the instance monitor, as documented.

Test signals: `TestBackgroundService` verifies waiting for task completion and single-thread behavior. Component tests such as block deletion and disk balancer exercise subclasses and timeout logging.
