# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/quick_exit.c

Implements C11 `at_quick_exit()` and `quick_exit()`. Handlers are stored in a singly linked stack and registered under `__atexit_mutex` on threaded builds, so execution is in reverse registration order.

`quick_exit()` calls handlers and then `_Exit(status)`, bypassing normal `atexit()` processing and stdio cleanup. Handler execution itself is not locked and the code notes no C++ exception handling beyond a TODO.
