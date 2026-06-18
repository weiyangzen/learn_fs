# File Research: sources/os/linux/linux/io_uring/rsrc.c

Registered resource implementation for fixed files, registered user buffers, kernel-backed buffers, resource updates, buffer cloning, and fixed-buffer import into iterators.

Key responsibilities:
- Enforces memory accounting for pinned pages against `RLIMIT_MEMLOCK` and `mm_account->pinned_vm`.
- Allocates/frees resource nodes and resource tables.
- Registers, unregisters, and updates fixed-file tables.
- Registers, unregisters, and updates registered buffer tables.
- Pins user pages, coalesces huge-folio buffers, builds `bio_vec` arrays, and unpins/releases on teardown.
- Supports kernel-backed registered buffers from block request bvecs for `uring_cmd` providers.
- Imports fixed buffers or fixed iovec vectors into `iov_iter`.
- Clones registered buffers from another ring while sharing underlying mapped-buffer refs.
- Provides reusable vector allocation helpers.

Important data flows:
- File registration allocates a table, `fget()`s each fd, rejects io_uring files, creates `IORING_RSRC_FILE` nodes, installs fixed-file pointers, and sets the allocation bitmap.
- Buffer registration imports each iovec, validates address/length, pins pages, optionally coalesces folio entries, accounts pinned pages, builds bvecs, and stores an `IORING_RSRC_BUFFER` node.
- Resource update resets existing nodes before installing replacements; tags cause auxiliary CQEs when nodes are freed.
- Fixed import validates requested ranges inside the registered buffer, checks direction permissions, then builds a bvec iterator with optimized segment skipping.
- Clone buffers locks source and destination rings in address order, verifies shared accounting identity, refcounts source mappings, and replaces or creates the destination table.

Concurrency and locking:
- Resource table mutation requires `ctx->uring_lock` via register path or explicit submit locking.
- Buffer node lookup for request use increments node refs under submit lock and stores `req->buf_node`.
- Cloning two rings uses ordered double locking to avoid ABBA deadlocks.

Important invariants:
- Registered buffer ranges must be nonzero, <= 1 GiB, non-overflowing, and later fixed imports must remain inside the original range.
- Kernel-backed buffers carry `IO_REGBUF_F_KBUF` and have direction limited by request direction.
- Tags are invalid on sparse/empty resource entries.
- Cloned buffers share `io_mapped_ubuf` accounting and therefore require identical user/mm accounting targets.

Notable risks:
- Huge-page accounting avoids double-counting compound heads across current and previously registered buffers.
- User page pin failure paths must unpin all pages already acquired and free partially allocated nodes.
- `io_import_reg_vec()` may reallocate the shared vector storage because converted bvecs can require more slots than the original user iovec list.
