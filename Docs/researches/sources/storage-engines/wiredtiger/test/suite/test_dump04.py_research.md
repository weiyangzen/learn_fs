# sources/storage-engines/wiredtiger/test/suite/test_dump04.py

Purpose: tests `wt dump -j` JSON output combined with `-k` key filtering.

Important APIs and control flow: creates a byte-array key/value table with three records. Helpers format expected plain or JSON/unicode strings, assert file contains or omits key/value pairs, and load the output through `json.load` for validity. `run_test` builds dump args with optional `-j` and `-k`.

State and persistence: checkpoint flushes dirty pages before utility dumps. The output file is inspected across JSON and non-JSON formats.

Dependencies and integration: uses `suite_subprocess`, `json`, file content regex helpers, and `wt dump`.

Risks and test signals: catches JSON escaping issues, key filtering with matching and non-matching keys, and invalid JSON. The method name `check_valid_jason` is misspelled but functional.
