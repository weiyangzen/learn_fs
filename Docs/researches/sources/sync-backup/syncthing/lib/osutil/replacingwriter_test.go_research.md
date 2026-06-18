## sources/sync-backup/syncthing/lib/osutil/replacingwriter_test.go

Purpose: tests `ReplacingWriter` behavior for simple string substitutions.

Important test/data: `testcases` define input, `from`, `to`, and expected output. `TestReplacingWriter` writes each input to a buffer through `ReplacingWriter` and compares output.

Control flow and state: table-driven, single-write cases.

Dependencies and integration points: validates text replacement helper but not `LineEndingsWriter` platform behavior.

Risks: does not test split replacement sequences across multiple writes or underlying writer errors.

Test signals: basic substitution coverage.
