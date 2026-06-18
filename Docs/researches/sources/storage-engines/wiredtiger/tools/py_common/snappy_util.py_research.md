# sources/storage-engines/wiredtiger/tools/py_common/snappy_util.py

Purpose: handles WiredTiger page payload decompression for pages compressed with Snappy and provides detailed diagnostics when decompression fails.

Important APIs and control flow: import-time detection sets `HAVE_SNAPPY`. `snappy_decompress_page()` preserves the uncompressed prefix up to the 64-byte compression skip, reads WiredTiger's stored compressed byte count, calculates the remaining block length, reads enough bytes for either interpretation, seeks to the end of the disk block, and tries Snappy validation/decompression first with the stored length and then with calculated length. On failure it calls `print_snappy_diagnostics()` and returns only the uncompressed prefix. `decode_snappy_varint()` parses Snappy's uncompressed-length varint. `print_snappy_diagnostics()` logs compressed sizes, expected uncompressed size, and selected backreference/output-position details from `snappy.UncompressError`.

State and persistence behavior: mutates the `BinaryFile` read position to the end of the page block. It does not write persistent state. Diagnostics go to logging and some lower-level code may print via the page decoder.

Dependencies and integration points: imported by `btree_format.WTPage.parse()` for compressed pages. `wt_binary_decode.feature_check()` warns when Snappy support is missing. It requires `python-snappy` when compressed pages must be decoded.

Risks: missing Snappy support raises `ModuleNotFoundError` from `snappy_decompress_page()` and may terminate the top-level file decode. Failed decompression returns partial page bytes rather than a hard failure, so callers may continue with incomplete data. The stored-vs-calculated length fallback is diagnostic-friendly but may mask format drift if both happen to decode.

Test signals: no direct Snappy tests are in this subset. Runtime signal is successful compressed-page decoding plus absence of feature-check warnings when `python-snappy` is installed.
