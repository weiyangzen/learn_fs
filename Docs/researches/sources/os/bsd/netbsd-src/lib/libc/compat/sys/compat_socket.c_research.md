# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_socket.c

Read completely: 27 lines.

This implements compatibility `socket` by calling `__socket30`. If `errno` is `EAFNOSUPPORT`, it remaps it to `EPROTONOSUPPORT`.

Security/reliability notes: the errno remap is unconditional after the call rather than guarded by failure, which relies on normal libc convention that callers inspect errno only when the return value indicates error.
