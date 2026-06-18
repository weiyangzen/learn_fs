# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_bio.c

## Purpose
Implements NetBSD's buffer cache: block buffer lookup, allocation, free-list management, synchronous/asynchronous block I/O, delayed writes, memory pressure trimming, I/O completion, nested I/O buffers, and buffer-cache sysctls.

## Main Interfaces
- Initialization: `biohist_init`, `buf_setvalimit`, `bufinit`, `bufinit2`.
- Buffer lookup/allocation: `incore`, `getblk`, `geteblk`, `allocbuf`, `getnewbuf`.
- Reads/writes: `bread`, `breadn`, `bwrite`, `vn_bwrite`, `bdwrite`, `bawrite`.
- Release/reclaim: `brelse`, `brelsel`, `bremfree`, `binvalbuf`, `buf_drain`, `buf_trim`.
- Completion: `biowait`, `biodone`, `biodone2`, `biointr`.
- Memory helpers: `buf_memcalc`, `buf_lotsfree`, `buf_canrelease`, `buf_alloc`, `buf_mrelease`.
- Sysctl/debug: `sysctl_dobuf`, `sysctl_bufvm_update`, `bufhash_stats`, optional `vfs_bufstats`.
- I/O-only buffers: `getiobuf`, `putiobuf`, `nestiobuf_setup`, `nestiobuf_iodone`, `nestiobuf_done`.
- Object lifecycle/locking: `buf_init`, `buf_destroy`, `bbusy`, `buf_nbuf`.

## State And Control Flow
Buffers are indexed by vnode/logical block in `bufhashtbl`, protected by `bufcache_lock`. Free buffers live on `BQ_LOCKED`, `BQ_LRU`, or `BQ_AGE` queues, with per-queue byte totals. `BC_BUSY` is the long-term buffer lock, while `b_objlock` protects I/O completion state and points to either the vnode interlock or global `buffer_lock`. `getblk` finds or creates a buffer, makes it busy, associates it with a vnode, and resizes memory. Read helpers call `VOP_STRATEGY` if data is not already valid; writes handle delayed-write state, WAPBL interactions, mount statistics, and sync/async completion.

## Dependencies And Integration
Tightly integrates VFS vnodes, block-device mounts, WAPBL journaling hooks, filesystem COW hooks (`fscow_run`), UVM kernel memory allocation, pool caches, soft interrupts, sysctl, DTrace SDT probes, and per-mount I/O accounting.

## Risks And Edge Cases
- Lock order is explicitly `bufcache_lock -> b_objlock`; violating it risks deadlock.
- `getnewbuf` may start delayed writes and return `NULL`, forcing callers to retry.
- The pagedaemon has special behavior to avoid deadlock when buffers are already busy or memory is unavailable.
- `allocbuf` changes both buffer size and global `bufmem`, then may trigger reclaim under memory pressure.
- I/O completion from interrupt context is deferred to a soft interrupt; callbacks, async release, and waiters take different paths.
- WAPBL-tracked buffers require resize/add/remove handling to preserve transaction accounting.

## Filesystem Relevance
Very high. This is core block-buffer infrastructure used by local filesystems for metadata and data block I/O.
