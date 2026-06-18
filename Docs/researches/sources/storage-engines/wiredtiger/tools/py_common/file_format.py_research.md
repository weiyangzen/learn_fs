# sources/storage-engines/wiredtiger/tools/py_common/file_format.py

Purpose: decodes ordinary WiredTiger `.wt` file objects or fragments into human-readable pages and optional CSV page statistics.

Important APIs and control flow: `file_header_decode()` parses `BlockFileHeader`, logs header fields, and validates magic, major/minor version, and unused bytes. `outfile_header()` writes CSV column names when `DecodeOptions.output` is present. `wtdecode_file_object()` creates a `Printer`, validates the file header when decoding from offset zero, aligns to the first block after a valid header, then loops over page starts until the byte limit or page limit is reached. Each iteration seeks to `startblock`, prints the decode address, parses a `WTPage`, prints page data or headers depending on options, emits CSV stats when available, and advances either to the parser's current position or by one 512-byte block to avoid stalling.

State and persistence behavior: input file position is mutated during scanning. Optional CSV output is appended to the passed output handle. The decoder has no repository or database persistence.

Dependencies and integration points: used by `wt_binary_decode.decode_wt_binary_input()` and `mdb_log_parse` for hex-dump fragments. It depends on `binary_data.d_and_h`, `btree_format.BlockFileHeader`, `btree_format.WTPage`, `Printer`, `DecodeOptions`, and `PageStats`.

Risks: on missing `python-snappy`, `ModuleNotFoundError` triggers `exit(1)`, which is abrupt for library callers. Generic decode exceptions are swallowed after logging and the scanner advances, so failures may be easy to miss unless verbose logging is enabled. Fragment handling relies on `opts.offset`, `opts.disagg`, and the parser position being sensible. CSV output has no quoting and assumes integer/string fields do not contain commas.

Test signals: `test_decode_page.py` validates page and block header fields from a known hex dump. Higher-level tests through `wt_binary_decode.wtdecode()` cover dump-in and disaggregated modes.
