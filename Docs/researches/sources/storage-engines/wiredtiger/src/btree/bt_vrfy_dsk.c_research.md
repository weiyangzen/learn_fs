# sources/storage-engines/wiredtiger/src/btree/bt_vrfy_dsk.c

## Purpose
`bt_vrfy_dsk.c` performs physical disk-image verification for individual btree pages. It checks page headers, flags, versions, record-number rules, trailing bytes, page/cell type compatibility, safe cell unpacking, key ordering, prefix compression, timestamp validity, address validity, fast-delete metadata, column-store run-length encoding opportunities, and overflow/data chunk boundaries.

## Important APIs, Types, And Functions
- `__wt_verify_dsk_image` verifies one disk image with optional parent address/time aggregate context and flags.
- `__wt_verify_dsk` is a convenience wrapper for a `WT_ITEM` buffer using continue-on-failure behavior.
- `WT_VERIFY_INFO` carries the session, page tag, disk header, optional address, page size, current cell number, and verify flags.
- `__verify_dsk_row_int`, `__verify_dsk_row_leaf`, `__verify_dsk_col_int`, `__verify_dsk_col_var`, and `__verify_dsk_chunk` are page-type-specific validators.
- `__verify_dsk_addr_validity`, `__verify_dsk_value_validity`, and `__verify_dsk_addr_page_del` validate time aggregates/windows and fast-delete metadata.
- `__wti_cell_type_check` is exported and shared with logical verification to validate legal cell/page combinations.

## Control Flow
`__wt_verify_dsk_image` initializes `WT_VERIFY_INFO`, validates page type, validates whether `dsk->recno` is required or forbidden for the page type, masks allowed page flags, rejects invalid flag combinations, checks reserved bytes and page version, ensures bytes after `mem_size` are zero when a full size is available, checks non-empty page/data rules, and dispatches to a type-specific scanner.

Each scanner walks cells using `WT_CELL_FOREACH_VRFY`, a verify-specific loop that does not trust cells until `__wt_cell_unpack_safe` succeeds within the page boundary. Row internal pages enforce alternating key/address cells, no prefix or recno/rle fields, key count equal to half physical entries, address validity, block-manager address validity, optional fast-delete metadata validation, and sorted internal keys except for the special 0th key. Row leaf pages enforce key/value ordering, value time-window validity, overflow address validity, prefix-compression reconstruction, sorted keys, and empty-value flag consistency. Column internal pages validate address cells and their referenced addresses. Column variable pages validate values, overflow addresses, and detect adjacent identical values/deletes that should have been run-length encoded. Chunk pages validate `datalen` and zero trailing bytes.

## State And Persistence Behavior
This code is read-only and does not modify btree state. Its persistence relevance is that it validates the exact serialized on-disk representation before in-memory page construction or during verify. It treats block-manager `addr_invalid` returning `EINVAL` as corruption/nonexistent file page evidence. `WT_SESSION_QUIET_CORRUPT_FILE` suppresses error printing but not validation failure.

## Dependencies And Integration Points
The module integrates with low-level cell unpacking, page headers, btree collators, block-manager address validation, time aggregate/value validation, scratch buffers for printable key diagnostics, and diagnostic breakpoint/error reporting. Logical verification in `bt_vrfy.c` relies on the physical validation boundary so it can assume the in-memory page was built from a structurally safe disk image.

## Risks
The code intentionally handles untrusted bytes; any unchecked cell length or pointer arithmetic error can turn corruption into memory unsafety. Error policy differs between ordinary verification, salvage, quiet corrupt file mode, and continue-on-failure flags. Row key ordering must reconstruct prefix-compressed keys exactly, including mixed overflow and prefix-compressed keys. Fast-delete timestamp validation must combine page-delete data with the cell aggregate correctly or it may reject valid truncates or miss invalid ones.

## Test Signals
Test cases should cover invalid page types/versions/flags, wrong record-number presence, non-zero reserved/trailing bytes, empty page rejection and allowed empty pages, cell unpack boundary failures, illegal cell/page combinations, row adjacent key/value ordering errors, prefix compression count overflow, unsorted keys under custom collators, invalid block addresses, fast-delete metadata inconsistencies, invalid timestamp windows, column RLE missed opportunities, and overflow chunk length overrun.
