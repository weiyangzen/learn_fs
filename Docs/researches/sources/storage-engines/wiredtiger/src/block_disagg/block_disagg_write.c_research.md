# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_write.c

## Purpose
Implements disaggregated page writes and discards. It builds disaggregated block headers, computes checksum chains, writes base or delta images through the page-log provider, packs address cookies, updates block metadata and size accounting, and forwards discard requests to the page log.

## Important APIs, types, and functions
- `__wti_block_disagg_write_size` adds disaggregated header space and rejects oversized writes.
- `__wti_block_disagg_write_internal` writes the buffer through `plh_put` and updates `WT_PAGE_BLOCK_META`.
- `__wti_block_disagg_write` is the vtable write path that byteswaps page headers, updates size accounting, and packs address cookies.
- `__wti_block_disagg_page_discard` decodes an address cookie, updates size accounting for non-root pages, and calls `plh_discard` when available.
- `__wt_block_disagg_header_byteswap_copy` and `__block_disagg_header_byteswap` are endian placeholders.
- `__block_disagg_addr_flags` encodes delta-chain status into address-cookie flags.

## Control flow
The high-level write path casts `WT_BLOCK` to `WT_BLOCK_DISAGG`, byteswaps the page header into storage order, calls the internal writer, increments the live block size by the stored size, restores the page header, and packs a `WT_BLOCK_DISAGG_ADDRESS_COOKIE`. For base images the cookie size is the block size. For deltas it is prior cumulative size plus this block size, and `block_meta->cumulative_size` is updated for future deltas.

The internal writer clears and fills the disaggregated block header, validates the buffer size, asserts the node is the layered-table leader, sets data-checksum/compression/encryption/base/delta/version fields, stores `previous_checksum`, computes the checksum, maps block metadata into `WT_PAGE_LOG_PUT_ARGS`, sets cold/compressed/encrypted/delta flags, calls `plh_put`, updates stats and histograms, logs verbose write details, and copies the returned LSN and checksum into `block_meta`.

Discard unpacks the cookie, logs it, subtracts size for non-root pages, tolerates missing `plh_discard`, and otherwise sends base/backlink LSNs to the page-log discard hook. For delta chains the discard base LSN is the cookie's `base_lsn`; for base images it is the page's own LSN.

## State and persistence behavior
The persisted block header stores magic, version, compatible version, checksum, previous checksum, data-checksum flag, compression/encryption flags, and base/delta identity. The address cookie stores page ID, LSNs, checksum, flags, and cumulative size. `WT_PAGE_BLOCK_META` is the mutable bridge from reconciliation to page log: it carries page ID, previous checksum, base LSN, backlink LSN, delta count, cumulative size, and receives the new disaggregated LSN/checksum after the write.

## Dependencies and integration points
This file depends on btree storage tier, layered-table leadership state, page-log `plh_put`/`plh_discard`, page-header byteswapping, address pack/unpack helpers, block size accounting, connection statistics, history-store flags, and checkpoint code that calls `__wti_block_disagg_write_internal` directly for root pages.

## Risks and edge cases
- Writes assert leader status; follower writes indicate a serious layered-table routing bug.
- Page headers are byteswapped in place and restored by the wrapper; direct internal writes must manage page-header order themselves.
- Checksum logic depends on whether full data checksums are requested and on compression skip semantics.
- Root discards deliberately skip size decrement because checkpoint root accounting is handled at checkpoint-pack time.
- Missing `plh_discard` is only a warning, so storage reclamation may be unavailable without failing the caller.

## Test signals
Tests should cover base writes, delta writes, compressed/encrypted flags, cold-tier flags, checksum validation on subsequent reads, cumulative size tracking, leader-only assertions, write-size overflow rejection, root versus non-root discard accounting, discard with and without provider support, and checkpoint root writes through the internal API.
