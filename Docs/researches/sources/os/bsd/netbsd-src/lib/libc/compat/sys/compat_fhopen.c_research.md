# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_fhopen.c

Read completely: 56 lines.

This implements old `fhopen` by passing the legacy `compat_30_fhandle` and fixed `FHANDLE30_SIZE` to `__fhopen40`.

Security/reliability notes: direct wrapper; downstream file-handle validation controls errors and permissions.
