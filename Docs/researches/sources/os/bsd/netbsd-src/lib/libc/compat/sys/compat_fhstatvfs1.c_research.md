# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_fhstatvfs1.c

Read completely: 60 lines.

This implements old `fhstatvfs1`, like `fhstatvfs` but preserving the caller-supplied flags argument. It converts the returned native `statvfs` to `statvfs90`.

Security/reliability notes: no local allocation; depends on the newer syscall wrapper for validation.
