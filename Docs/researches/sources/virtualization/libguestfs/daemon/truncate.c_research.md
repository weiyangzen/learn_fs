# File Research: sources/virtualization/libguestfs/daemon/truncate.c

## Role
Implements file truncation actions inside the guest filesystem.

## Main Operations
- `do_truncate_size()` opens a guest path under `CHROOT_IN`, calls `ftruncate()` to the requested size, and closes the file.
- `do_truncate()` truncates to zero by delegating to `do_truncate_size()`.

## Error Handling
Open, truncate, and close failures are reported with the guest path.

## Filesystem/Storage Relevance
This provides direct guest file size manipulation, affecting file allocation and sparse-file behavior depending on the underlying filesystem.
