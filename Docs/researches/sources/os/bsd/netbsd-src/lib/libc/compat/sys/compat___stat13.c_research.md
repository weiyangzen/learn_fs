# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___stat13.c

Read completely: 140 lines.

This implements `__stat13`, `__fstat13`, `__lstat13`, and old `fhstat` aliases. Each calls the corresponding `*50` current stat wrapper, then converts native `struct stat` to `struct stat13` by narrowing device, inode, rdev, and timestamp seconds to older fields.

Important interactions: `fhstat` passes a hard-coded old file-handle size of 28 bytes to `__fhstat50`.

Security/reliability notes: field narrowing can truncate inode/device/time values. The conversion is deterministic and allocation-free.
