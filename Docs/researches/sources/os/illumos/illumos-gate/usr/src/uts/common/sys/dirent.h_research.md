# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dirent.h

This header defines filesystem-independent directory entry structures and `getdents` large-file interface mapping. It includes feature-test definitions.

`dirent_t` contains inode number, directory offset, record length, and variable-length name. A kernel syscall32 `dirent32_t` form uses 32-bit inode/off_t fields. Under `_LARGEFILE64_SOURCE`, `dirent64_t` uses 64-bit inode and offset fields.

Kernel/fake-kernel helpers compute aligned record length and name length for 64-bit and 32-bit dirent layouts. `MAXGETDENTS_SIZE` caps bytes stored by `getdents(2)` in user buffers at 64 KiB.

For userland, large-file compilation mappings redirect `getdents` to `getdents64` on ILP32 with `_FILE_OFFSET_BITS=64`, and map `getdents64`/`dirent64` back to native on LP64. The file declares `getdents(int, struct dirent *, size_t)` and deliberately does not provide a transitional large-file function declaration.

Research notes:
- This is user ABI and kernel ABI for directory entry record layout.
- Alignment macros are important for filesystem `getdents` implementations.
- Feature-test macros control visible names and large-file symbol mapping.
