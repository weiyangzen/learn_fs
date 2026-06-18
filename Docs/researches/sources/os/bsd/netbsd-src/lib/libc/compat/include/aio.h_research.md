# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/aio.h

Declares compatibility AIO timeout interfaces.

It forward-declares `struct aiocb`, `struct timespec50`, and `struct timespec`, then declares old `aio_suspend` using `timespec50` and modern `__aio_suspend50` using `timespec`.

This supports time32/time64 ABI translation for asynchronous I/O.
