# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/atexit.c

Read completely: 281 lines.

Implements `atexit()`, `__cxa_atexit()`, optional ARM `__aeabi_atexit()`, `__cxa_finalize()`, and a startup initializer for the recursive atexit mutex. Handlers are stored in a LIFO stack of `struct atexit_handler`; normal `atexit` handlers can use a static pool of 35 descriptors before falling back to malloc, while C++ ABI DSO-tied handlers always use allocated descriptors.

`__cxa_finalize(dso)` runs all handlers for `dso` or all handlers when `dso == NULL`, supports recursive finalization, marks handlers as consumed before invocation, restarts if new handlers are registered during execution, and frees dynamic descriptors after the outermost call. `__cxa_atexit()` asserts that DSO-bound callers pass a non-null DSO handle.
