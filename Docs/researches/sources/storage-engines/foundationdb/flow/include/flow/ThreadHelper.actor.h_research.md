<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ThreadHelper.actor.h -->
# sources/storage-engines/foundationdb/flow/include/flow/ThreadHelper.actor.h

Purpose: This actor header provides thread-to-network-thread bridging primitives and thread-safe future-like values. It lets side threads schedule work on the Flow main thread, wait for thread futures, convert thread futures to actor futures, and publish thread-safe async variable changes.

Important APIs and types: Key APIs are `onMainThreadVoid`, `onMainThread`, `ThreadCallback`, `ThreadMultiCallback`, `ThreadSingleAssignmentVarBase`, `ThreadSingleAssignmentVar<T>`, `ThreadFuture<T>`, `unsafeThreadFutureToFuture`, `safeThreadFutureToFuture`, `ThreadSafeAsyncVar<V>`, and `ThreadResult<T>`. Helper callbacks include `CompletionCallback` and `UtilCallback`.

Control flow: `onMainThreadVoid` creates a signal promise, starts an actor waiting on it, and schedules the signal on `g_network->onMainThread`. `ThreadSingleAssignmentVar` stores one value, error, or never-set state under a spin lock; callbacks either fire immediately if ready or are registered. `ThreadFuture` references the SAV and can block, get, cancel, or register callbacks. Safe conversion to `Future<T>` schedules a main-thread wakeup when the thread future is ready and propagates cancellation both ways.

State and persistence behavior: All state is in-memory synchronization state: SAV status, error, value, callback chain, cancel future, value reference count, and async-var current/next-change values. No persistence is involved. For `Standalone<T>` values, the header explicitly prevents unsafe anonymous future conversion because memory can live in the `ThreadFuture`.

Dependencies and integration points: It depends on actor compiler support, Flow futures/promises/errors, `ThreadPrimitives`, `g_network`, task priorities, and trace logging. It is used by thread pools, blocking APIs, and any side-thread code that must safely re-enter the actor network thread.

Risks: Blocking on the network thread throws `blocked_from_network_thread`; callers must avoid deadlocks. `unsafeThreadFutureToFuture` is documented as not actually thread safe and lacks cancellation. Callback management is intricate, especially with multi-callback holder linked lists. Cancellation intentionally sometimes schedules on the main thread for performance and safety, so ownership assumptions matter.

Test signals: Tests should cover send value/error/never, double-fulfillment assertions, blocking waits from side threads, blocked wait on main thread, callback add/clear/multi-callback behavior, safe conversion cancellation in both directions, `Standalone` conversion guard behavior, `ThreadSafeAsyncVar` change notifications, and `ThreadResult` ready-only semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ThreadHelper.actor.h -->
