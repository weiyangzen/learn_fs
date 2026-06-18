# File Research: sources/os/linux/linux/block/bio-integrity-auto.c

`bio-integrity-auto.c` automatically generates and verifies block integrity metadata for bios whose submitter did not provide protection information. It lets the kernel use PI-capable devices even when the filesystem or bio submitter is not explicitly PI-aware.

Data model:
- `struct bio_integrity_data` wraps the target bio, saved data iterator, deferred work item, embedded `bio_integrity_payload`, and one bio_vec.
- A slab cache and mempool provide allocation reliability.
- `kintegrityd_wq` runs verification in process context.

Preparation:
- `bio_integrity_prep()` allocates `bio_integrity_data`, initializes the bio’s integrity payload, marks `BIP_BLOCK_INTEGRITY`, allocates an integrity buffer, sets default guard/ref-tag checks when requested, and either generates metadata for writes or saves the data iterator for later read verification.
- It exports `bio_integrity_prep`.

Completion:
- `__bio_integrity_endio()` is called on integrity I/O completion.
- For successful reads with check flags, it queues work to verify metadata asynchronously and returns false to delay `bio_endio()`.
- Otherwise it finishes immediately and returns true.
- `bio_integrity_verify_fn()` performs verification, stores the resulting block status in `bio->bi_status`, frees integrity state, and ends the bio.
- `bio_integrity_finish()` detaches and frees payload/buffer state and clears `REQ_INTEGRITY`.

Initialization:
- `blk_integrity_auto_init()` creates the slab, initializes the mempool, and allocates a high-priority CPU-intensive per-cpu workqueue named `kintegrityd`.
- `blk_flush_integrity()` flushes the workqueue.
- Init runs as `subsys_initcall`.

Important behavior:
- Verification is intentionally deferred out of interrupt context because it may be CPU-expensive.
- Writes generate integrity metadata before submission; reads verify after completion.
