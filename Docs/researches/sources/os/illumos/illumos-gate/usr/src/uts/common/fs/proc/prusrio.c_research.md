# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prusrio.c

## Purpose

`prusrio.c` implements `prusrio()`, the low-level helper for reading from or writing to a target process address space through procfs-style user I/O.

## Behavior

`prusrio(proc_t *p, enum uio_rw rw, struct uio *uiop, int old)` transfers `uiop->uio_resid` bytes starting at `uiop->uio_offset`.

For small transfers up to 64 bytes it uses a stack buffer. Larger transfers allocate one page of kernel memory. Transfers are split at page boundaries with:

- `len = MIN(uiop->uio_resid, PAGESIZE - (addr & PAGEOFFSET))`

For reads:

1. `uread()` copies from the target process into the kernel buffer.
2. `uiomove(..., UIO_READ, uiop)` copies from the kernel buffer to the caller.

For writes:

1. `uiomove(..., UIO_WRITE, uiop)` copies caller data into the kernel buffer.
2. `uwrite()` writes the buffer into the target process.
3. If `uwrite()` fails after `uiomove()`, the function backs up `uio_resid` and `uio_loffset` by the attempted length.

On SPARC, if the target is `curproc`, it flushes register windows to the stack before accessing user memory.

## Error Handling

`ENXIO` means the target page did not exist. The function maps this as follows:

- Reads: if some data was transferred, or if using new semantics (`old == 0`), return success; otherwise return `EIO`.
- Writes: if some data was transferred, return success; otherwise return `EIO`.

Unexpected `rw` values panic.

## Dependencies

This helper depends on `uread()`, `uwrite()`, `uiomove()`, `kmem_alloc()`, `kmem_free()`, and SPARC register-window flushing when applicable. It is intentionally page-boundary aware so partial failures have predictable procfs behavior.
