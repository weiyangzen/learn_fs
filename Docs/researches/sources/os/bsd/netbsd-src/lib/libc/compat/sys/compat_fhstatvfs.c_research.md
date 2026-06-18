# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_fhstatvfs.c

Read completely: 59 lines.

This implements old `fhstatvfs`, calling `__fhstatvfs190` with legacy handle size and flags `0`, then converting native `statvfs` to `statvfs90`.

Security/reliability notes: direct conversion wrapper; field narrowing is delegated to the statvfs converter.
