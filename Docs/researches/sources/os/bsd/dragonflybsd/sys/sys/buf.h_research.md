# File Research: sources/os/bsd/dragonflybsd/sys/sys/buf.h

Read completely: 501 lines.

This header defines the kernel buffer-cache buffer object, BIO queue structures, flags, and public buffer-cache APIs.

Key contents:
- `buf_cmd_t` command enum for read, write, free blocks, format, flush, seek, and done.
- `struct buf` with vnode index trees, free/cluster links, vnode pointer, embedded BIO layers, flags, queue CPU/index, activity counters, buffer lock, command, sizes, residual/error, KVA/data pointers, dirty range, reference count, xio page list, bio ops, and dependency/private union.
- Logical and physical BIO aliases `b_bio1`, `b_bio2`, and `b_loffset`.
- `getblk`/`findblk` flags and a large set of `B_*` buffer state flags.
- BIO queue and cluster-save structures.
- `clrbuf()` helper and allocation/sequence constants.
- Kernel externs and prototypes for buffer lifecycle, read/write, clustering, pbufs, BIO stack, completion, physical I/O, VM page integration, nested I/O, and diagnostics.

Important interactions:
- Used by VFS, VM, filesystem, and block-device layers.
- Comments define strict layering: strategy routines should operate on the passed BIO, not directly on `bp->b_vp`.

Security/reliability notes:
- Buffer flags are highly stateful; invalid combinations can cause lost writes, stale cache data, or bad VM page state.
- `B_KVABIO` requires explicit KVA synchronization before direct `b_data` access across CPUs.
