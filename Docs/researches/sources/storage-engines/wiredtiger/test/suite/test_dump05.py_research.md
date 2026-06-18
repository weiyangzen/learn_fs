# sources/storage-engines/wiredtiger/test/suite/test_dump05.py

Purpose: validates JSON formatting from `wt dump -j` for string and byte-array tables with many variable-length records.

Important APIs and control flow: `validate_json_dump` creates a table, writes 1000 random-length key/value suffixes, runs `wt dump -j`, then uses regex file checks to ensure no junk appears after closing quotes and valid key/value JSON records exist. It runs once for `key_format=S,value_format=S` and once for `key_format=u,value_format=u`.

State and persistence: output is utility-generated JSON. Random record lengths stress buffer reuse and termination boundaries.

Dependencies and integration: uses `suite_subprocess`, Python `random`, and file regex helpers.

Risks and test signals: it is focused on output cleanliness rather than parsing with `json.load`. Failures point to stale buffer bytes, quote handling, or JSON field formatting regressions.
