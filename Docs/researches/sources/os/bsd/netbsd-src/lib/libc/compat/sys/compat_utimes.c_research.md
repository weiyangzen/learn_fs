# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_utimes.c

Read completely: 88 lines.

This implements old `utimes`, `lutimes`, and `futimes` using arrays of two `timeval50` values. If the array is non-null, it converts both access and modification times, then calls the corresponding `*50` wrapper; otherwise it forwards null.

Security/reliability notes: array callers must provide two valid entries. Null means “use current time” behavior is preserved.
