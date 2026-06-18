# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_subr.c

Purpose: Provides miscellaneous kernel support routines: safe user copy wrappers, `uio` movement, one-byte uio read helper, generic hash table allocation, and hook lists.

Key behavior:
- Under `PMAP_CHECK_COPYIN`, `copyinstr()` and `copyin()` call `check_copyin()` to reject ranges overlapping protected VM map regions.
- `uiomove()` copies between kernel buffers and user/kernel iovecs, respecting `uio_rw`, `uio_segflg`, residual count, offset, and iovec advancement.
- `ureadc()` emits one byte into a `uio`, advancing iovec/resid/offset.
- `hashinit()` rounds element count to a power of two, allocates an array of LIST heads, initializes them, and returns a hash mask.
- `hashfree()` frees the corresponding rounded hash table allocation.

Hooks:
- `startuphook_list` is globally initialized.
- `hook_establish()` allocates and inserts a hook at head or tail.
- `hook_disestablish()` removes and frees a hook.
- `dohooks()` runs hooks, optionally removing and freeing them.

Filesystem relevance:
- `uiomove()` is central to read/write paths across filesystems and devices.
- `copyin()` and `copyinstr()` gate user pointers used by syscall and path-handling code.
- `hashinit()` is a common primitive for vnode/inode/cache tables.
