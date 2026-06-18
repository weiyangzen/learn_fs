# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___fhstatvfs140.c

Read completely: 59 lines.

This implements `__fhstatvfs140`, forwarding a file handle and explicit length to `__fhstatvfs190`, then converting current `struct statvfs` to legacy `statvfs90` on success.

Important interactions: compatibility wrapper for the statvfs ABI version that still carried a flags argument but old output layout.

Security/reliability notes: allocation-free; correctness depends on `statvfs_to_statvfs90` handling field narrowing.
