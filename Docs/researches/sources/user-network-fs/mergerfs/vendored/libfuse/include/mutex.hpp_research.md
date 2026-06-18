<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex.hpp

Purpose: This header selects debug or non-debug pthread mutex wrappers and provides RAII helpers around `pthread_mutex_t`.

Important APIs: `mutex_t` is `pthread_mutex_t`. `Mutex` initializes/destroys a mutex and converts to `mutex_t&`. `LockGuard` locks in its constructor and unlocks in its destructor. The `mutex_lockguard(m)` macro uses a scope guard to lock and defer unlock while preserving call-site file/function/line for debug builds.

State and integration: each `Mutex` owns one pthread mutex. The wrappers are used by object pools, thread vectors, and other low-level shared state.

Risks and test signals: `mutex_lockguard` expands to statements and must be used carefully in control-flow contexts. Copying `Mutex` is not explicitly deleted, so accidental copies would duplicate a pthread mutex object unsafely. Tests should cover debug and release builds, RAII unlock on exceptions, and misuse in single-line `if` statements during review.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex.hpp -->
