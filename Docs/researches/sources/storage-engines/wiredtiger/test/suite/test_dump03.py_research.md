# sources/storage-engines/wiredtiger/test/suite/test_dump03.py

Purpose: verifies `wt dump -k KEY -w WINDOW` returns the requested key plus a symmetric window around it, clipped at table boundaries.

Important APIs and control flow: scenarios specify key, window size, and expected data line count. The test populates `key1` through `key99`, runs `wt dump -k <key> -w <winsize>`, then counts lines after the `Data` header.

State and persistence: table content is stable during a single utility run. Output line count is the validation surface, with two lines per record.

Dependencies and integration: uses `suite_subprocess`, `make_scenarios`, and utility dump output.

Risks and test signals: boundary scenarios at start/end and zero window catch off-by-one errors in window expansion and clipping.
