<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor08.py

Purpose: tests log cursors when the log itself uses compression.

Important APIs and control flow: scenarios combine reopen/no-reopen with log compressors `nop`, `snappy`, `zlib`, and `none`. `conn_config()` enables compressed logging and dsync; `conn_extensions()` loads the compressor when needed. The test writes 500 string values containing control characters in one transaction, optionally reopens, scans `log:`, and counts log records whose value bytes contain the encoded payload.

State, persistence, and dependencies: persistent state is compressed log records and a table. Dependencies are compressor extension loading, log cursor record layout, transaction sync, and Python string-to-byte encoding.

Integration points: covers log compression/decompression visibility through the public log cursor interface.

Risks and test signals: missing compressor extensions skip scenarios. Pass signal is exact recovery of all expected values through log cursor after optional reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor08.py -->
