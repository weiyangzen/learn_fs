# File Research: sources/os/linux/linux/block/bio-integrity-fs.c

`bio-integrity-fs.c` provides filesystem-facing helpers for generating and verifying integrity metadata on bios. It is separate from automatic PI handling and gives filesystem submitters explicit helper calls.

Data model:
- `struct fs_bio_integrity_buf` embeds a `bio_integrity_payload` and one `bio_vec`.
- A slab cache and mempool back allocations.

Allocation/free:
- `fs_bio_integrity_alloc()` computes the needed action via `bio_integrity_action()`. If none is needed, it returns zero. Otherwise it allocates an integrity buffer object, initializes the bio integrity payload, allocates backing metadata storage, applies default check flags, and returns the action mask.
- `fs_bio_integrity_free()` frees the metadata buffer, returns the wrapper to the mempool, clears `bio->bi_integrity`, and clears `REQ_INTEGRITY`.

Generation and verification:
- `fs_bio_integrity_generate()` allocates integrity metadata if needed and then calls `bio_integrity_generate()`. It is exported GPL.
- `fs_bio_integrity_verify()` rebuilds the integrity iterator after driver completion using the remembered sector and size, computes metadata size from the disk integrity profile, and returns an errno converted from `bio_integrity_verify()` status.

Initialization:
- `fs_bio_integrity_init()` creates the slab and mempool at `fs_initcall`.

Important behavior:
- Verification requires the caller to remember the original sector and size because the submitter uses this helper after the driver has advanced bio state.
- The helper assumes the bio still carries the integrity payload allocated earlier.
