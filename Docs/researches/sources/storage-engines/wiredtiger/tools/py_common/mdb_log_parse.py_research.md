# sources/storage-engines/wiredtiger/tools/py_common/mdb_log_parse.py

Purpose: extracts raw WiredTiger block bytes from text logs, supporting both MongoDB structured JSON log entries and WiredTiger-style hex dumps, then sends the bytes through the page decoder as fragments.

Important APIs and control flow: `process_logs()` peeks at the first line and routes JSON-looking input to `process_mongod_log()` or other input to `process_wiredtiger_log()`. `extract_mongodb_log_hex()` scans JSON lines for `__wt_bm_corrupt_dump` messages, parses `{offset, size, checksum}: (chunk N of M): hexdata`, validates characters and expected byte size, and returns the first complete block. `encode_bytes()` decodes line-oriented hex dump chunks from the current file position, respecting optional chunk counters. `HexDumpCorruptError`, `validate_hexdata()`, and `validate_hex_block_size()` separate corrupt dump diagnostics from incidental parse failures.

State and persistence behavior: no persistent writes. File objects are advanced as blocks are consumed; JSON decode fallback can seek back to the start and parse as ordinary hex. Decoded bytes are transient `bytearray`/`bytes` buffers.

Dependencies and integration points: depends on `json`, `re`, `codecs`, `binary_data.BinaryFile`, `DecodeOptions`, and `file_format.wtdecode_file_object()`. It is selected by `wt_binary_decode` when `--dumpin` is passed and is directly used by `test_decode_page.py`.

Risks: MongoDB log detection is simply `line.startswith('{')`, so non-Mongo JSON logs may enter the structured parser. Regexes are tailored to current checksum-mismatch log text. Incomplete MongoDB blocks are returned with a warning rather than rejected. `encode_bytes()` strips all non-hex characters from the payload part, which is useful for noisy logs but can also decode unintended hex-looking text.

Test signals: `test_decode_log_mongodb.py` verifies corrupt non-hex, odd-length, and block-size-mismatch diagnostics; valid and incomplete cases are currently skipped under FIXME-WT-16726. `test_decode_page.py` uses `encode_bytes()` to decode `WiredTiger01.txt`.
