# sources/storage-engines/wiredtiger/tools/wt_ckpt_decode.py

Purpose: decodes WiredTiger checkpoint address cookies from hex strings into root/extent offsets, sizes, checksums, and disaggregated root-page address fields.

Important APIs and control flow: `usage()` and `err_usage()` handle CLI help. `show_one()` and `show_ref()` format numeric fields with decimal and hex. `decode_arg()` converts a hex argument to bytes, treats version byte `1` as ordinary WT checkpoint format and other leading bytes as disaggregated format, unpacks as many integers as possible using `unpack_int()`, validates expected counts, and prints either four address cookies plus file/checkpoint size for regular/tiered checkpoints or root page id/LSN/checkpoint id/record id/size/checksum for disaggregated address cookies. CLI option `-a` sets allocation size, defaulting to 4096.

State and persistence behavior: pure stdout decoder; no input files or persistent writes.

Dependencies and integration points: depends on `py_common.binary_data.unpack_int()` and WiredTiger checkpoint cookie format. It is a standalone diagnostic script.

Risks: disaggregated detection assumes any first byte other than version `1` is a disagg cookie. Error handling for invalid hex or unpack failures is minimal. The `--allocsize` long option is declared without explicit `=` handling but only `-a` is implemented in the option loop.

Test signals: no automated tests in this subset. Commented sample address cookies provide manual smoke cases for regular, tiered, disagg 5-entry, disagg 6-entry, and bad formats.
