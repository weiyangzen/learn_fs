<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config06.py

Purpose: validates `session.create` format configuration edge cases for key/value formats and disaggregated storage-tier restrictions.

Important APIs and control flow: `bad_session_config()` asserts invalid create configs. Tests reject unsupported `A` formats and zero-length string formats, then `format_string()` creates fixed-length `S`/`s` key/value formats of lengths 1, 4, and 10, inserts longer strings, and verifies truncation behavior. Default `S` and `s` behavior is checked separately. One test asserts ASC rejects `disaggregated=(storage_tier=cold)` outside the disagg hook.

State, persistence, and dependencies: each success path creates a single table and stores one key/value pair. Dependencies include `wiredtiger`, `wttest`, cursor indexing, and hook decorators.

Integration points: covers create-time format parsing, string truncation semantics, and disaggregated configuration validation.

Risks and test signals: fixed-length byte/string semantics differ between `S` and `s`, and Python string handling can hide truncation mistakes. Pass signals are invalid argument errors for bad formats and exact truncated values for valid fixed-length formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config06.py -->
