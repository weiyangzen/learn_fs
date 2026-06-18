# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___fhstatvfs40.c

Read completely: 58 lines.

This implements `__fhstatvfs40`, forwarding to `__fhstatvfs190` with flags `0` and converting current `statvfs` to `statvfs90`.

Important interactions: old ABI for file-handle statvfs without a flags parameter.

Security/reliability notes: direct conversion wrapper; downstream syscall reports errors.
