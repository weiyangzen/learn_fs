# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/lang/RunnableCallable.java

## Purpose
`RunnableCallable` adapts a `Runnable` to `Callable<Void>` and a `Callable<?>` to `Runnable`. The scheduler service uses it to expose one scheduling API for both task forms.

## Important APIs, types, and functions
The constructors accept either a `Runnable` or `Callable<?>` and reject nulls through `Check.notNull`. `call()` invokes the wrapped task and returns null. `run()` invokes the wrapped runnable directly or wraps callable exceptions in `RuntimeException`. `toString()` returns the wrapped class simple name.

## Control flow
Each instance has exactly one non-null delegate. Invocation paths branch on whether the runnable field is set; otherwise the callable field is used.

## State and persistence behavior
State is limited to object references. No persistent state or background resource is owned.

## Dependencies and integration points
It depends on `java.util.concurrent.Callable` and the local `Check` utility. `SchedulerService.schedule(Runnable, ...)` wraps runnables with this class before delegating to the callable scheduler.

## Risks and edge cases
The callable-to-runnable path converts checked exceptions into unchecked `RuntimeException`, so callers using `run()` lose checked exception typing. `toString()` assumes anonymous classes still have a useful simple name, which may be empty.

## Test signals
No direct tests in this subset. Scheduler tests or instrumentation counters would expose adapter failures when runnable tasks are scheduled.
