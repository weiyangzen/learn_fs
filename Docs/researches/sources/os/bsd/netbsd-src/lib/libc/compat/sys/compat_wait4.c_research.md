# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_wait4.c

Read completely: 84 lines.

This implements old `wait3` and `wait4` returning `rusage50`. Both call current `__wait350`/`__wait450` with a native `rusage` temporary when requested, then convert resource usage back on success.

Security/reliability notes: direct process wait wrapper; rusage field narrowing follows the conversion helper.
