## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/grpc/AsyncTaskExecutor.h

Purpose: Implements a lightweight Flow-compatible task executor backed by `IThreadPool`, used primarily to offload blocking gRPC work.

Important APIs/types/functions: `IsVoidReturn` is a C++20 concept distinguishing void-return tasks. `AsyncTaskExecutor` creates a generic thread pool with a requested number of receiver threads, stops it in the destructor, and exposes `post()` overloads for non-void tasks returning `Future<R>` and noexcept void tasks returning nothing. Internal `Action<Func>` specializations implement `ThreadAction` for non-void and void tasks.

Control flow: Posting asserts the caller is on the main network thread, wraps the callable in a heap-allocated `ThreadAction`, and submits it to the pool. Non-void actions execute the function, send result through `ThreadReturnPromise`, convert Flow `Error` or unknown exceptions to future errors, then delete themselves. Void actions execute a noexcept function and delete themselves.

State and persistence behavior: State is the executor-owned thread pool and per-action heap objects/promises. No durable state.

Dependencies and integration points: Depends on Flow network-thread checks and `IThreadPool`. Used by `AsyncGrpcClient` and potentially other blocking integrations.

Risks: Void tasks must be nothrow by API constraint; throwing would violate assumptions. Posted lambdas can outlive captured objects. The executor destructor stops the pool, so callers need clear ownership around in-flight tasks. Simulation determinism requires careful thread count choices.

Test signals: Non-void success and exception propagation, void task execution, main-thread assertion, destructor stop behavior, multiple thread execution, and simulation mode with one thread.
