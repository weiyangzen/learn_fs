<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex_debug.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex_debug.hpp

Purpose: This debug-mode wrapper instruments pthread mutex operations with call-site-aware error reporting and timed-lock notices.

Important APIs and flow: macros `mutex_init`, `mutex_destroy`, `mutex_lock`, and `mutex_unlock` expand to underscored functions with file/function/line. Initialization uses `PTHREAD_MUTEX_ADAPTIVE_NP` where available. Locking loops with `pthread_mutex_timedlock` using 1 ms deadlines, printing a notice on each timeout until the lock is acquired or an error aborts the process.

State and integration: state is the pthread mutex itself; diagnostics go to stderr through fmt. This file is included by `mutex.hpp` when `DEBUG` is defined.

Risks and test signals: repeated timeout logging can be noisy under legitimate contention, and abort-on-error is intentionally fatal. Tests should cover successful lock/unlock, destroy errors in a subprocess, and contention diagnostics without deadlocking the test suite.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex_debug.hpp -->
