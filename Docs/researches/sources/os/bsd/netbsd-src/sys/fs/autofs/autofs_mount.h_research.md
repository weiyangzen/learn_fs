# File Research: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_mount.h

## Summary
Defines the public mount argument structure for AUTOFS.

## Main Responsibilities
- Define `struct autofs_args` with map source `from`, `master_options`, and `master_prefix`.

## Integration Notes
The VFS mount path copies these user strings into `struct autofs_mount`.
