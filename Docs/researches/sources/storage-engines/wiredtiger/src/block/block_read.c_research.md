# sources/storage-engines/wiredtiger/src/block/block_read.c

## Purpose

`block_read.c` implements physical block reads for file-backed block handles. It unpacks address cookies, reads aligned disk blocks, validates checksums, swaps headers to native endian order, reports corruption, optionally diagnoses single-bit flips, and dumps filesystem free-space and extent-list context on checksum failures.

## Important APIs, Types, and Functions

Key functions are `__wt_bm_read`, `__wt_bm_corrupt`, diagnostic `__wt_block_read_off_blind`, `__wti_block_read_off`, and private `__block_bitflip_detect` plus `__fs_free_space_dump`. It consumes `WT_BLOCK_HEADER`, `WT_PAGE_HEADER`, `WT_BM`, `WT_BLOCK`, and address-cookie fields `(objectid, offset, size, checksum)`.

## Control Flow

`__wt_bm_read` unpacks the address cookie, resolves a tiered/multi-handle object if needed, runs diagnostic misplaced-block checks, delegates to `__wti_block_read_off`, discards OS cache when configured, and releases tiered read handles. `__wti_block_read_off` validates minimum size, allocates the destination buffer, throttles read capacity, reads from the file handle, byte-swaps a copy of the block header, chooses full-data versus prefix checksum based on `WT_BLOCK_DATA_CKSUM`, clears the stored checksum before recomputation, and swaps the page header before returning.

On mismatch, it logs differentiated full-checksum or header-checksum messages, dumps the corrupt block, dumps free disk space, optionally searches for a single-bit flip, sets connection data-corruption state, returns `WT_ERROR` for verify/quiet-corrupt paths, or panics during normal reads.

## State and Persistence Behavior

Normal reads do not mutate durable state, but they update connection statistics, session buffers, read histograms, and OS cache-discard counters. Corruption paths set `WT_CONN_DATA_CORRUPTION` and may emit diagnostic data dumps. Multi-handle reads manipulate `block->read_count` through tiered handle acquisition/release and can trigger handle sweeping after the last release.

## Dependencies and Integration Points

This code is below `block_cache/block_io.c` and the `WT_BM.read` method table. It uses block address packing/unpacking, file-system reads, capacity throttling, checksum utilities, verbose logging, diagnostic extent-list dumping from `block_ext.c`, tiered handle management from `block_tier.c`, and log-manager paths for journal free-space diagnostics.

## Risks and Edge Cases

Read sizes smaller than allocation size are rejected. Partial checksums intentionally protect only the uncompressed/unencrypted prefix, so upper layers must correctly decompress/decrypt. `__block_bitflip_detect` mutates the buffer while testing and restores each bit; it is bounded by `WT_BITFLIP_MAX_SIZE` to avoid excessive CPU. Quiet corruption and verify modes must not panic. Multi-handle release must happen on all read paths to avoid preventing tiered-handle sweeping.

## Test Signals

Useful tests include checksum mismatch paths, compressed/encrypted checksum mode behavior, diagnostic blind reads, quiet-corrupt verify reads, single-bit-flip detection through the unit-test shim, free-space logging when the file-system hook succeeds or fails, and stats `block_read`, `block_byte_read`, `block_map_read`, and read latency histograms.
