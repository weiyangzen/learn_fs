# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/getenv.c

Read completely: 112 lines.

Implements `getenv()` and `getenv_r()`. Both validate the requested name with `__envvarnamelen()`, acquire the environment read lock, locate the variable with `__findenvvar()`, and release the lock.

`getenv()` returns the live environment value pointer. `getenv_r()` copies into a caller buffer with `strlcpy()`, returning `0` on success and `-1` with `ENOENT` or `ERANGE` on failure.
