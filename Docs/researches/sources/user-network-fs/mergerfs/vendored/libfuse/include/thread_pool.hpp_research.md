<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/thread_pool.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/thread_pool.hpp

Purpose: `ThreadPool` is a pthread-backed work queue for FUSE processing. It uses `BoundedQueue<ofats::any_invocable<void()>>` to limit normal work backlog while allowing unbounded internal control messages.

Important APIs and flow: the constructor blocks signals while spawning workers, names threads when requested, and throws if none start. Workers wait on queue tokens, disable cancellation while executing a task, catch/log ordinary exceptions, clear the callable, then re-enable cancellation. Public methods add/remove/set thread count, enqueue work with or without producer tokens, try/timed enqueue work, enqueue future-returning tasks, snapshot thread IDs, and create producer tokens.

State and integration: state includes queue, pool name, pthread vector, and a `Mutex` protecting the vector. Destructor cancels and joins all known threads. `remove_thread` enqueues a control task that erases its own thread ID, sets a promise, and exits.

Risks and test signals: `pthread_cancel`-based shutdown relies on workers being in cancellation-enabled regions, so long-running tasks delay destruction. `enqueue_task` uses `std::invoke_result_t<FuncType>` without explicit argument list, suitable only for nullary callables. Tests should cover queue backpressure, dynamic resize, exception logging, future results/exceptions, thread naming length, destructor with idle and busy workers, and signal mask behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/thread_pool.hpp -->
