# File Research: sources/os/bsd/freebsd-src/sys/sys/buf.h

## Purpose
`buf.h` defines the FreeBSD kernel buffer-cache buffer header, buffer flags, locking helpers, and the VFS buffer I/O function surface.

## Main Interfaces
- `struct buf` describes cached or active filesystem/block I/O: associated `bufobj`, sizes, data pointer, BIO command/flags, offsets, residual count, callbacks, checksum hash, vnode links, queue state, locks, dirty ranges, VM pages, credentials, cluster/dependency state, optional tracking, and extended errors.
- `B_*`, `BX_*`, and `BV_*` flags describe buffer lifecycle, cache validity, delayed writes, clustering, VMIO, background writes, vnode clean/dirty list state, and filesystem-private state.
- Buffer lock macros wrap `lockmgr`, including timed locks, unlock assertions, ownership transfer to kernel process for async I/O, and invariant assertions.
- Inline helpers call bufobj operations (`bwrite`, `bstrategy`) and softdep-style `bioops` hooks (`buf_start`, `buf_complete`, `buf_deallocate`, `buf_countdeps`).
- Declares bread/getblk/write/release/cluster/vmap/page-busy and vnode association APIs.

## Implementation Notes
The header documents field protection domains: buffer lock, owning `bufobj` lock, queue lock, or dependency-specific lock. `b_bcount` is the requested valid range, while `b_bufsize` is allocation size. Dirty ranges are byte-granular and normally clipped at `b_bcount`.

## Dependencies and Constraints
Most APIs are kernel-only. Buffer correctness depends on honoring lock ownership, not mixing incompatible flags such as `B_INVALONERR` with async use, and using `bufobj` operation vectors for strategy/write dispatch.
