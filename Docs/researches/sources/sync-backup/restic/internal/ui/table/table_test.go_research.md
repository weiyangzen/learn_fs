# sources/sync-backup/restic/internal/ui/table/table_test.go

Purpose: exact-output regression tests for table rendering.

Important APIs/types/functions: one table-driven `TestTable` builds several `Table` instances and compares `Write()` output to expected strings.

Control flow: each case creates columns/rows/footers, writes to `bytes.Buffer`, trims the leading newline from the expected raw string, and reports a side-by-side mismatch.

State and persistence: no external state; all output is in memory.

Dependencies/integration: relies on `strings.TrimLeft` and Go testing. It indirectly verifies `text/template`, the `join` template helper, and `ui.DisplayWidth` through expected padding.

Risks: tests are intentionally brittle for spacing. They do not cover custom printer callbacks returning errors or template execution errors.

Test signals: strong coverage for empty output, separators, padded headers, multi-row tables, multi-column alignment, multi-line cells, footers, and non-ASCII display width.
