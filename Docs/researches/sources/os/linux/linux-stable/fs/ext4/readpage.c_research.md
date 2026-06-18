# File Research: sources/os/linux/linux-stable/fs/ext4/readpage.c

## Summary
Implements ext4 read-folio and readahead paths. It maps logically contiguous file blocks into read bios, handles fscrypt decryption and fsverity verification as post-read processing, falls back to buffer-head reads for complex page layouts, and manages a mempool for post-read contexts.

## Main Responsibilities
- Read single folios and readahead windows for ext4 files.
- Prefer multipage bio reads for contiguous mapped blocks.
- Detect holes and zero-fill them.
- Fall back to `block_read_full_folio()` for buffer-backed folios, hole-then-data layouts, or non-contiguous blocks.
- Attach fscrypt and fsverity post-read processing to bios.
- Verify fsverity data for hole-only folios when applicable.
- Initialize and destroy post-read processing caches and mempools.

## Key Data Structures
- `enum bio_post_read_step`: ordered post-read pipeline: decrypt, then verity.
- `struct bio_post_read_ctx`: carries bio, verity info, work item, current step, and enabled step mask.
- `bio_post_read_ctx_cache` / `bio_post_read_ctx_pool`: slab cache and mempool guaranteeing post-read context allocation.

## Key Functions
- `__read_end_io()`: ends read on every folio in a bio, frees post-read context, and drops the bio.
- `decrypt_work()`: runs fscrypt bio decryption and continues or fails completion.
- `verity_work()`: frees the context before fsverity verification to avoid mempool recursion deadlock, verifies the bio, and completes it.
- `bio_post_read_processing()`: advances through decrypt and verity steps using separate workqueues.
- `mpage_end_io()`: bio completion entry; dispatches post-read processing when needed or completes reads directly.
- `ext4_set_bio_post_read_ctx()`: attaches a guaranteed-allocated post-read context when fs-layer crypto or fsverity is needed.
- `ext4_readpage_limit()`: uses `s_maxbytes` for verity files and `i_size` for normal files.
- `ext4_mpage_readpages()`: core mapping and bio-building loop for folio reads and readahead.
- `ext4_read_folio()`: VFS read-folio operation; handles inline data, fsverity prefetch, and mpage read.
- `ext4_readahead()`: VFS readahead operation; skips inline data and dispatches mpage reads with optional fsverity prefetch.
- `ext4_init_post_read_processing()` / `ext4_exit_post_read_processing()`: manage post-read context cache and mempool.

## Read Mapping Behavior
`ext4_mpage_readpages()` keeps a reusable `ext4_map_blocks` result across folios. For each folio it:
- Rejects folios that already have buffers and falls back.
- Maps up to the current read limit.
- Allows holes only at the end of a folio.
- Requires mapped blocks in a folio to be contiguous.
- Marks fully mapped folios as mapped-to-disk.
- Merges adjacent physical blocks into bios when fscrypt merge rules permit.
- Submits the current bio on physical discontinuity, fscrypt incompatibility, extent boundary, or partial-hole folio.

## Encryption and Verity
Bios for encrypted files get fscrypt block-crypto context. If fs-layer crypto is required, decryption is scheduled after I/O. If fsverity applies, verification runs after decryption. Separate workqueues are used so verity metadata reads that require decryption do not recurse into the same queue.

## Dependencies
Depends on ext4 block mapping, folio APIs, bios, blk-crypto submission, fscrypt, fsverity, buffer-head fallback reads, readahead control, and ext4 tracepoints.

## Risks and Edge Cases
- The mpage path intentionally avoids complex folio completion cases involving multiple non-contiguous bios; it falls back to buffer-head reads instead.
- Hole-only folios in verity files still require verification before successful completion.
- Post-read context allocation uses a mempool because completion paths can require nested reads.
- Verity uses `s_maxbytes` as a read limit so Merkle tree verification can operate correctly beyond normal data EOF semantics.
