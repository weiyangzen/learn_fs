# sources/storage-engines/wiredtiger/tools/test/test_decode_log_mongodb.py

Purpose: tests MongoDB JSON log hex-dump validation and error logging for corrupt checksum-mismatch dumps.

Important APIs and control flow: `setUp()` records the binary fixture directory. `run_decode()` captures stdout and `py_common.mdb_log_parse` INFO logs while calling `wt_binary_decode.wtdecode(log_path, DecodeOptions(dumpin=True))`. Three active tests assert diagnostics for non-hex characters, odd-length hex, and block-size mismatch. Valid, multi-chunk valid, incomplete-chunk, and no-checksum-mismatch tests are present but skipped under FIXME-WT-16726.

State and persistence behavior: read-only over log fixtures; captures output/logs in memory.

Dependencies and integration points: exercises `wt_binary_decode` dump-in routing and `mdb_log_parse.extract_mongodb_log_hex()` corruption paths.

Risks: most positive-path coverage is skipped, leaving successful MongoDB log extraction under-tested. Assertions depend on exact log message substrings. The helper captures INFO logs but not DEBUG details that could aid diagnosis.

Test signals: active tests confirm corrupt input returns no valid byte dump and logs the specific validation error class.
