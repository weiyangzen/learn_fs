# sources/storage-engines/wiredtiger/test/suite/test_jsondump02.py

Purpose: direct JSON cursor and JSON dump/load coverage for strings, byte arrays, column groups, indexes, malformed JSON, and byte escaping. Both test methods are currently skipped due to a known JSON cursor failure.

Important APIs and functions: `test_jsondump02` extends `WiredTigerTestCase` and `suite_subprocess`. Helpers `set_kv`, `set_kv2`, `populate_squarecube`, `check_json`, `load_json`, `generate_key`, `generate_value`, and `bytes_to_str` build and validate JSON cursor data. It uses cursors opened with `dump=json` and utility calls `wt dump -j`/`wt load -jf`.

Control flow: `test_json_cursor` would create several tables plus column groups and indexes, insert special strings/unicode/byte data, validate JSON cursor output, truncate/load JSON back, check many malformed-token/type/order errors, dump/load tables through utility files, and revalidate. `test_json_all_bytes` would generate 256 byte-array/string cases, validate JSON escaping, round-trip through JSON cursors and utility files.

State and persistence behavior: intended coverage includes in-memory JSON cursor conversion and persistence through dump/load files. It also checks index and column-group JSON projections.

Dependencies and integration points: integrates JSON parser/serializer, WiredTiger dump/load utility, Unicode escaping, byte-array formats, indexes, colgroups, and subprocess harness.

Risks and edge cases: both tests call `skipTest('Known failure in JSON cursor')`, so current suite execution records skips rather than coverage. If re-enabled, many exact error-message and escaping expectations may need maintenance.

Test signals: current signal is intentional skip. When enabled, exact JSON key/value strings, expected parser errors, and dump/load round trips are the signals.
