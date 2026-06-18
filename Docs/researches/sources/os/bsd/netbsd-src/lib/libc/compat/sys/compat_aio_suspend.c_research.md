# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_aio_suspend.c

Read completely: 70 lines.

This implements old `aio_suspend` with a `timespec50` timeout. It converts the optional timeout and delegates to `__aio_suspend50`.

Important interactions: leaves the aiocb list unchanged; only the timeout ABI differs.

Security/reliability notes: no heap allocation; timeout null is supported.
