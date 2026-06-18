<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cell_inline.h -->
# sources/storage-engines/wiredtiger/src/include/cell_inline.h

## Purpose
Implements inline packing, unpacking, validation, cleanup, data-reference, and iteration helpers for the cell format defined in `cell.h`. It is the main bridge between in-memory MVCC/page structures and bytes stored in WiredTiger page images.

## Important APIs, Types, and Functions
Validation and packing helpers include `__cell_check_value_validity`, `__cell_assert_tw_has_ts_for_garbage_collection_table`, `__cell_pack_value_validity`, `__wt_check_addr_validity`, `__cell_pack_addr_validity`, `__wt_cell_pack_addr`, `__wt_cell_pack_value`, `__wt_cell_pack_copy`, `__wt_cell_pack_del`, `__wt_cell_pack_int_key`, `__wt_cell_pack_leaf_key`, and `__wt_cell_pack_ovfl`.

Prefix and image-building helpers include `__wt_cell_compress_prefix_key`, `__wt_cell_decompress_prefix_key`, `__wt_cell_pack_leaf_kv`, `__wt_cell_build_addr_kv`, `__cell_build_int_key_from_kv`, `__wt_cell_kv_copy`, `__wt_cell_pack_internal_key_addr`, and `__wt_cell_build_addr`.

Type and length helpers include `__wt_cell_rle`, `__wt_cell_total_len`, `__wt_cell_type`, `__wt_delta_cell_type_visible_all`, `__wt_cell_type_raw`, `__wt_cell_type_reset`, and `__wt_cell_leaf_value_parse`.

Unpack helpers include `__wt_cell_unpack_safe`, `__wt_cell_unpack_addr`, `__wt_cell_unpack_kv`, `__wt_cell_unpack_delta_leaf_value`, plus internal address/value window decoders and cleanup helpers.

Data access helpers include `__wt_cell_get_ta`, `__wt_cell_get_tw`, `__wt_dsk_cell_data_ref_addr`, `__wt_dsk_cell_data_ref_kv`, and `__wt_page_cell_data_ref_kv`. Iterator macros include delta leaf, delta internal, base internal, address, and key/value foreach forms.

## Control Flow
Packing starts with a zero descriptor byte, optionally emits validity/aggregate metadata through a second descriptor byte, optionally emits RLE or recno, emits packed data length when needed, and returns the header length. Short key/value cells avoid the length varint when size fits in six descriptor bits.

Value-window packing stores timestamps and transaction IDs compactly, often as deltas from the start timestamp or transaction. Prepared starts/stops are encoded into timestamp/durable fields, with additional prepared ID storage when `WT_CONN_PRESERVE_PREPARED` is enabled. Address aggregate packing follows similar delta encoding and can mark prepared fast truncation.

Unpacking normalizes raw cell variants into common fields. It handles short cells directly, decodes optional prefix bytes and second-descriptor windows, reads RLE/recno, resolves `WT_CELL_VALUE_COPY` by jumping backward to the source cell while preserving the current cell's RLE/window/length, and computes the full cell length for iteration. Safe unpacking can enforce an end pointer for verification.

Restart cleanup checks page write generations against the btree base write generation and clears persisted transaction IDs while preserving timestamp semantics. This cleanup applies to both key/value windows and address aggregates, including fast-truncate page delete metadata.

Data-reference helpers either point at on-page data or read overflow items through `__wt_ovfl_read`. The disk-only KV accessor asserts it is not asked to read removed overflow cells; the page-aware accessor can use page context for lookaside/cached overflow handling.

## State and Persistence Behavior
The functions produce and interpret persistent page bytes, including transaction/timestamp visibility and fast-truncate state. They also mutate unpacked in-memory structures during restart cleanup by clearing transaction IDs and setting `WT_CELL_UNPACK_TIME_WINDOW_CLEARED` so reconciliation can rebuild cells. Image-building helpers append bytes to caller-owned `WT_ITEM` buffers and update delta merge state such as entry counts and last key.

## Dependencies and Integration Points
Depends on timestamp/window validators, varint packing/unpacking, `WT_TIME_WINDOW`, `WT_TIME_AGGREGATE`, `WT_PAGE_DELETED`, `WT_PAGE_HEADER`, `WT_CELL_KV`, `WT_ITEM`, buffer helpers, overflow read, structured unpacking, B-tree flags, write generations, and disaggregated merge state. It integrates with reconciliation, page read/verify, row/column cell iteration, delta page merge, truncate, prepared transaction recovery, dictionary compression, overflow item handling, and garbage-collection tables.

## Risks and Edge Cases
This file is format-critical. Incorrect flag ordering, delta arithmetic, or prepared ID placement can make existing page images unreadable or corrupt MVCC visibility. The comments call out `FIXME-WT-14887` around pointer memory safety in `__wt_cell_kv_copy` and `FIXME-WT-17663` for passing correct prepared-fast-truncate state in internal key/address packing. `WT_CELL_VALUE_COPY` requires careful length preservation or page iteration will desynchronize. Restart cleanup must not erase timestamp semantics while clearing non-persistent transaction IDs. Verification paths rely on `WT_CELL_LEN_CHK` to prevent out-of-bounds reads.

## Test Signals
High-value tests include cell pack/unpack round trips, verify with truncated/corrupt cells, timestamp window validation, prepared update recovery with preserve-prepared, fast truncate and prepared fast truncate, overflow read/remove behavior, dictionary value copies, row prefix compression/decompression, delta leaf/internal merge, restart cleanup across write generations, and garbage-collection table timestamp assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cell_inline.h -->
