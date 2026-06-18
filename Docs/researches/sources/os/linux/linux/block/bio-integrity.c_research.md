# File Research: sources/os/linux/linux/block/bio-integrity.c

`bio-integrity.c` implements core bio integrity payload allocation, user metadata mapping, cloning/trimming, metadata buffer allocation, and default integrity action selection.

Action selection:
- `__bio_integrity_action()` decides what integrity work a bio needs based on operation and disk integrity profile.
- Reads may need buffering and verification unless `BLK_INTEGRITY_NOVERIFY` allows offload-only behavior.
- Writes skip zero-sector flush-like bios, may need zeroed metadata when generation is disabled, and may need guard/ref-tag checks depending on metadata tuple size.
- Bios with crypto context are rejected for integrity action.

Buffers and defaults:
- `bio_integrity_alloc_buf()` allocates a contiguous integrity buffer sized by `bio_integrity_bytes()`, falling back to a mempool page on allocation failure.
- `bio_integrity_free_buf()` frees kmalloc or mempool-backed storage.
- `bio_integrity_setup_default()` seeds integrity metadata from the bio sector and sets guard, IP checksum, and ref-tag check flags from the disk integrity profile.

Payload allocation:
- `bio_integrity_init()` attaches an existing payload and bvec array to a bio and sets `REQ_INTEGRITY`.
- `bio_integrity_alloc()` allocates a flexible payload with `nr_vecs` integrity segments and exports it.
- `bio_integrity_free()` frees the allocated payload and clears bio integrity state.

User metadata mapping:
- `bio_integrity_map_user()` maps an iov_iter carrying user integrity metadata.
- It rejects preexisting integrity state, too-large metadata, and excessive vector counts.
- It extracts pages from the iterator, handles partial pinning failure, coalesces pages into bvecs, detects P2PDMA pages, and decides whether a bounce copy is needed due to DMA alignment or segment limits.
- `bio_integrity_copy_user()` bounces metadata through kernel memory; for reads it preserves original bvecs for copying data back on completion, and for writes it copies user data in and unpins original pages.
- `bio_integrity_init_user()` attaches pinned user bvecs directly.
- `bio_integrity_unmap_user()` unpins direct mappings or copies read metadata back from bounce buffer and frees bounce state.

`uio_meta` integration:
- `bio_integrity_map_iter()` validates a `uio_meta` object, limits the iterator to metadata matching the current bio’s data sectors, maps it, transfers guard/app/ref tag flags, sets the seed, advances the original iterator, and increments the seed by integrity intervals.
- `bio_uio_meta_to_bip()` maps user integrity flags into `BIP_CHECK_*` flags and app tag.

Vector adjustment and cloning:
- `bio_integrity_advance()` advances integrity iterator state by the integrity bytes corresponding to completed data bytes.
- `bio_integrity_trim()` resets a cloned bio’s integrity size to match current bio sectors and is exported.
- `bio_integrity_clone()` allocates a clone payload that references the source integrity vectors and copies clone-safe flags and app tag.

Initialization:
- `bio_integrity_initfn()` initializes a page mempool sized for `BLK_INTEGRITY_MAX_SIZE`.
- Init runs as `subsys_initcall`.

Important behavior:
- Integrity metadata segment limits honor `queue_max_integrity_segments()`.
- Segment merging respects zone-device compatibility and SG gap constraints.
- P2PDMA metadata sets `REQ_NOMERGE`.
- Bounce-copy paths are used for DMA alignment/padding problems or excessive segment counts.
