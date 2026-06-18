# sources/storage-engines/wiredtiger/tools/py_common/btree_format.py

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/btree_format.py -->
## sources/storage-engines/wiredtiger/tools/py_common/btree_format.py

### Purpose
`btree_format.py` models and decodes WiredTiger on-disk B-tree/block formats for diagnostic tooling. It parses file headers, page headers, block headers, disaggregated-storage headers and address cookies, block-manager extent lists, row-page cells, timestamps, transaction ids, optional Snappy-compressed pages, CRC32C checksums, and BSON cell values.

### Important APIs, Types, and Functions
`BlockFileHeader`, `PageHeader`, `BlockHeader`, and `BlockDisaggHeader` parse fixed-format headers. `PageType`, `PageFlags`, `BlockFlags`, `BlockDisaggFlags`, `CellType`, and `DisaggAddrFlags` mirror WiredTiger enum/flag constants. `ExtentItem` parses block-manager extent records. `Cell.parse` decodes descriptor bytes, optional second descriptor/timestamps, run length/address values, key/value/overflow payload lengths, short cells, prefix cells, and disaggregated delta value flags. `DisaggAddr.parse` decodes packed page address cookies. `verify_block_checksum` validates CRC32C when the optional module is installed. `WTPage.parse` is the top-level page parser, while `print_page`, `print_cells`, `decode_rows`, and `decode_extlist` provide interpretation and display.

### Control Flow
`WTPage.parse` records disk position, reads the appropriate normal or disagg header bytes, validates unused fields/page type/size/checksum, optionally skips payload, reads or decompresses payload, then dispatches by page type. Block-manager pages decode extent lists until end marker or validation failure. Row internal/leaf pages decode `entries` cells and feed timestamp/key statistics. Printing later walks parsed structures and chooses raw bytes, BSON decode, or disaggregated address JSON according to options.

### State and Persistence
Decoded page state is held in a `WTPage` dataclass with headers, cells/extents, stats, success flag, and raw byte stream. `BinaryFile.saved` supports split raw-byte output. The module itself writes no files, but `Printer` and callers can emit decoded text/CSV stats.

### Dependencies and Integration Points
Depends on `py_common.binary_data`, `py_common.stats.PageStats`, `py_common.printer`, `py_common.snappy_util`, optional `crc32c`, and optional `bson`. It is designed for higher-level page/file decoders that provide a `BinaryFile` and `DecodeOptions`.

### Risks and Test Signals
Checksum zeroing assumes checksum bytes at offsets 32-35, which must match both normal and disagg layouts. `WTPage.print_page` uses `len(self.raw_bytes)` for overflow pages even though `BinaryFile` has no `__len__`, so that branch is suspect. Several cell types and overflow address details are marked TODO or treated unsupported; `ignore_unsupported=True` prevents hard failures in row decoding but may hide format drift. `Cell` size fields are annotated but not initialized in `__init__` unless corresponding timestamps exist, requiring `PageStats` to tolerate missing attributes. Tests should use binary fixtures for normal row leaf pages, compressed pages, checksum success/failure with and without `cont`, block-manager extent lists, disagg base/delta pages, timestamp windows, unsupported cell types, BSON decode, and truncated payloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/btree_format.py -->
