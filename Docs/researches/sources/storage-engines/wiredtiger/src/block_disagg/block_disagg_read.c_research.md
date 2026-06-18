# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_read.c

## Purpose
Implements disaggregated page reads through the page-log interface, including multi-buffer base-plus-delta fetch, block header validation, checksum/magic/version checking, page-header byteswap, metadata population, read statistics, debug reads by page ID, and corruption reporting.

## Important APIs, types, and functions
- `__wti_block_disagg_read_multiple` is the vtable read path for address-cookie referenced pages and deltas.
- `__block_disagg_read_multiple` calls `plh_get`, validates each returned buffer, and fills `WT_PAGE_BLOCK_META`.
- `__wti_block_disagg_read` returns `ENOTSUP`; single-buffer basic reads are not supported.
- `__wti_block_disagg_corrupt` reads and dumps block data for corruption diagnostics.
- `__wt_block_disagg_debug_read_page_id` fetches raw page-log results for debug tooling without validation/byteswap.
- `__block_disagg_check_lsn_frontier` warns if reads pass the materialization frontier.
- `__ut_block_disagg_header_version_compatible` exposes version compatibility to unit tests.

## Control flow
The public multi-read path unpacks a `WT_BLOCK_DISAGG_ADDRESS_COOKIE`, then calls the internal reader with page ID, flags, LSNs, cumulative size, and checksum. The internal reader builds `WT_PAGE_LOG_GET_ARGS`, tags cold storage when needed, increments read stats, checks the materialization frontier, and invokes `plh_get`. It expects one base image plus up to `WT_DELTA_LIMIT` deltas.

Validation walks results from newest delta back to base. For each buffer it copies the disaggregated header, treats nonzero modified-cache flags as cache-origin reads, checks the header checksum chain against the expected checksum, validates base/delta magic, validates compatible version, fills `WT_PAGE_BLOCK_META` from page-log get results on the newest buffer, byteswaps the page header, and then updates the expected checksum to `previous_checksum`. On mismatch it logs context, dumps data unless quiet corrupt mode is set, marks connection data corruption, and panics for ordinary reads.

## State and persistence behavior
Reads reconstruct page state from a page-log chain identified by `page_id`, `lsn`, `base_lsn`, size, flags, and checksum in the address cookie. `WT_PAGE_BLOCK_META` receives `page_id`, `backlink_lsn`, `base_lsn`, `disagg_lsn`, `delta_count`, `checksum`, and `cumulative_size`, allowing later reconciliation and delta writes to build on the read. The checksum chain through `previous_checksum` persists ordering assumptions between deltas and base images.

## Dependencies and integration points
This file depends on address unpacking, page-log `plh_get`, disaggregated block headers from the write path, page-header byteswap helpers, connection materialization frontier state, statistics, history-store/cold-storage flags, and debug btree tooling. It is installed as `WT_BM::read_multiple`; ordinary `read` intentionally fails.

## Risks and edge cases
- Single-block reads are unsupported, so all callers must use `read_multiple` for disaggregated btrees.
- Header version compatibility is one-way: a block whose `compatible_version` is newer than the reader is corrupt for this build.
- Modified victim-cache blocks skip part of the normal size/checksum assumptions, so validation differs from page-service reads.
- The read loop assumes result ordering with base at index 0 and deltas after it; page-log provider ordering bugs would corrupt reconstruction.
- Frontier violations currently warn and count stats rather than crash.

## Test signals
Tests should cover base-only reads, base-plus-delta chains, checksum-chain failures, wrong magic for base/delta, incompatible header versions, cold-tier reads, history-store reads, victim-cache modified blocks, materialization frontier warning stats, quiet corrupt behavior, and debug reads returning raw buffers without validation.
