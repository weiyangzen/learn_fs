<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex_ndebug.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex_ndebug.hpp

Purpose: This release-mode wrapper provides compact pthread mutex helpers that abort on pthread errors without formatted diagnostics.

Important APIs: `mutex_init` creates an adaptive mutex, `mutex_lock` locks, `mutex_unlock` unlocks, and `mutex_destroy` destroys. All functions call `std::abort()` if the pthread operation returns nonzero.

State and integration: it is selected by `mutex.hpp` when `DEBUG` is not defined. It owns no extra state beyond caller-provided pthread mutexes.

Risks and test signals: fatal aborts simplify error handling but make recovery impossible. Adaptive mutex availability is normalized to `PTHREAD_MUTEX_NORMAL` where missing. Tests should compile on Linux and FreeBSD-like environments and run basic lock/unlock/destroy paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex_ndebug.hpp -->
