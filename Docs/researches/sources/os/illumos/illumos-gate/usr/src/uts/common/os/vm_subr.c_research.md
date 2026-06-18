# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vm_subr.c

Provides VM and raw-I/O support routines: physical I/O setup, user access checking, and temporary kernel mapping of user pages with optional copy-on-write protection.

Key responsibilities:
- Implements `minphys()` to clamp buffer I/O size to `maxphys`.
- Creates a `physio_buf_cache` for reusable `struct buf` objects used by physical I/O.
- Implements `default_physio()` for raw character/block driver I/O through page locking and strategy submission.
- Provides legacy `useracc()` address permission checking.
- Provides `cow_mapin()` for temporarily borrowing user pages into kernel mappings, optionally protecting MAP_PRIVATE segvn pages with COW.

Important paths:
- `physio_bufs_init()` creates a `kmem_cache` whose constructor/destructor run `bioinit()` and `biofini()`.
- `default_physio()` allocates or reuses a buf, fills DTrace-visible metadata, walks `uio` iovecs, checks offsets, clamps size with `mincnt`, locks user/kernel pages with `as_pagelock()`, submits the driver strategy routine, waits with `biowait()`, unlocks pages, and advances iov/resid/offset.
- `useracc()` maps `B_READ`/write-style access into `as_checkprot()` with `PROT_USER`.
- `cow_mapin()` validates the target segment for optional COW, softlocks pages with `hat_softlock()`, optionally increments anon refcounts and read-protects user mappings, maps pages into kernel space with `hat_devload()`, reuses cached mappings when possible, and faults pages in once on `FC_NOMAP`.

Locking and memory model:
- `default_physio()` requires the buf semaphore to be held and uses `as_pagelock()` / `as_pageunlock()` around I/O.
- `cow_mapin()` holds the address-space writer lock during COW setup to prevent racing COW faults or anon teardown.
- `cow_mapin()` uses `HAT_NOCONSIST`/`HAT_LOAD_NOCONSIST` device-style mappings and requires the caller to handle cache-consistency responsibilities.

Filesystem relevance:
- Directly relevant to device and filesystem raw I/O paths. It bridges `uio`, buf strategy calls, page locking, DTrace I/O probes, and user-page mapping, all of which are used by storage drivers and special-file I/O below filesystems.
