# sources/sync-backup/git-lfs/tools/str_tools_test.go

Purpose: unit tests for string helper behavior.

Important APIs/types/functions: `QuotedFieldsTestCase`, `TestQuotedFields`, tests for `Longest`, `Rjust`, `Ljust`, `Indent`, and `Undent`.

Control flow: table-driven quote tests exercise leading/trailing whitespace, empty quoted fields, nested quote characters, and mixed quotes; remaining tests assert exact string outputs.

State and persistence: none.

Dependencies and integration points: uses `testify/assert`.

Risks: expected behavior documents a non-shell parser; future changes toward shell semantics would break many cases.

Test signals: good coverage for intended simple parsing/formatting semantics.
