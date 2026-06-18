# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/cxa_thread_atexit.c

Read completely: 88 lines.

Implements thread-local C++ destructor registration through `__cxa_thread_atexit_impl()` and destructor execution through `__cxa_thread_run_atexit()`. Destructors are kept in a thread-local `SLIST`; registration allocates a node, optionally increments the DSO reference count via `__dl_cxa_refcount()`, and inserts at the head.

`__cxa_thread_run_atexit()` pops and runs destructors in reverse registration order, decrements DSO references, and frees nodes. A weak alias exposes `__cxa_thread_atexit` for libstdc++ compatibility, and the global hidden flag `__cxa_thread_atexit_used` lets `exit()` know whether to run thread destructors.
