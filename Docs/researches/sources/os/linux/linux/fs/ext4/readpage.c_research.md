# File Research: sources/os/linux/linux/fs/ext4/readpage.c

## Purpose
Implements ext4 folio read and readahead using multipage BIOs with support for fs-layer decryption and fsverity verification. It replaces generic mpage behavior where ext4 needs post-read processing.

## Main Entry Points
- `ext4_read_folio()` handles single-folio reads, including inline data and fsverity setup.
- `ext4_readahead()` handles readahead batches.
- `ext4_mpage_readpages()` maps file blocks into efficient read BIOs.
- `ext4_init_post_read_processing()` / `ext4_exit_post_read_processing()` manage a mempool-backed post-read context cache.

## Read Path
`ext4_mpage_readpages()` iterates folios from either a readahead control or a single folio. It rejects folios that already have buffers, maps blocks with `ext4_map_blocks()`, reuses prior mappings, detects holes, zeros hole ranges, marks fully mapped folios, and builds BIOs only for contiguous physical runs. It falls back to `block_read_full_folio()` for complex cases such as hole-then-data, noncontiguous blocks within a folio, or existing buffers.

BIOs are split on physical discontinuity, fscrypt non-mergeability, extent boundaries, or partial-hole folios. Submitted BIOs carry blk-crypto context and optional post-read context.

## Post-Read Processing
Post-read work is modeled as ordered steps: decrypt then verity. `mpage_end_io()` either finishes folios directly or starts `bio_post_read_processing()`. Decryption runs on the fscrypt decrypt workqueue. Verity runs on the fsverity workqueue and frees the post-read context before verification to avoid mempool deadlock from recursive reads.

`__read_end_io()` ends each folio read according to BIO status, frees the post-read context if still attached, and drops the BIO.

## Integration Points
Uses ext4 block mapping, folio/readahead APIs, buffer-head fallback reads, fscrypt BIO contexts and decrypt work, fsverity info/readahead/verification, blk-crypto submission, and ext4 tracepoints.

## Invariants and Risks
The fast multipage path only handles simple contiguous block layouts. Holes after data are fine at EOF, but data after holes within a folio forces fallback. Verity reads may extend past `i_size` up to `s_maxbytes`, so `ext4_readpage_limit()` changes the read limit for verity inodes.

## Testing Signals
Cover inline-data reads, full-hole folios, EOF partial holes, noncontiguous fallback, encrypted reads, verity reads, encrypted+verity post-read ordering, readahead BIO splitting, and map error zero/unlock behavior.
