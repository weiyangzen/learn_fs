# File Research: sources/os/bsd/netbsd-src/sys/sys/buf.h

## Scope

Defines NetBSD kernel buffer headers, buffer flags, priority helpers, clustered I/O metadata, and buffer I/O/cache APIs.

## APIs And Data Structures

- `struct buf` describes kernel I/O buffers with driver queue linkage, callback, error/residual/count fields, device/block numbers, data pointers, vnode association, condition variables, and object lock.
- Field comments identify ownership locks: holder/busy owner, `bufcache_lock`, and `b_objlock`.
- Flags split into cache-owned `BC_*`, object-owned `BO_*`, and holder-owned `B_*`.
- Provides `BUF_ISREAD`, `BUF_ISWRITE`, `B_MEDIA_FLAGS`, and `clrbuf()`.
- Defines allocation/read hints `B_CLRBUF`, `B_SYNC`, `B_METAONLY`, `B_CONTIG`, `B_MODIFY`.
- Kernel APIs include `biodone`, `biowait`, `getiobuf`, `putiobuf`, nested I/O helpers, `physio`, `bread`, `breadn`, `bwrite`, `bawrite`, `bdwrite`, `getblk`, `geteblk`, `incore`, `allocbuf`, `brelse`, `binvalbuf`, `bufinit`, drain/limit helpers, and debug printing.
- Defines buffer I/O priority levels and access macros.

## Dependencies

- Includes pools, queues, mutexes, condition variables, rbtree, and kernel workqueue support.

## Risks And Invariants

- Lock ownership of fields is central to correctness.
- `B_WRITE` is a pseudo-flag equal to zero, so callers must use helper predicates.
- Union storage asserts `struct work` fits in queue storage.
