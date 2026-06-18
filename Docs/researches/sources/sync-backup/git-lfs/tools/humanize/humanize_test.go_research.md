# sources/sync-backup/git-lfs/tools/humanize/humanize_test.go

Purpose: table-driven tests for byte parsing and formatting.

Important APIs/types/functions: test-case structs for parse/format operations and tests `TestParseBytes`, `TestFormatBytes`, `TestParseByteUnit`, `TestFormatBytesUnit`, and `TestFormateByteRate`.

Control flow: each test iterates named cases and delegates assertions to a case method. Cases cover IEC and SI suffixes, case-insensitivity, spaces, rounding under/over/exact values, unknown units, non-second durations, and zero-duration rates.

State and persistence: no I/O or persisted state.

Dependencies and integration points: imports the external `humanize` package path, so it validates exported API behavior rather than internals. Uses `testify/assert`.

Risks: expected values encode decimal rather than binary formatting; changes to rounding semantics will require broad fixture updates. The test name has a typo (`Formate`).

Test signals: strong coverage for supported units and presentation boundaries, limited overflow coverage.
