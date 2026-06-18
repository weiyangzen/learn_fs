# sources/sync-backup/restic/internal/ui/table/table.go

Purpose: small table-rendering helper for aligned terminal output.

Important APIs/types/functions: `Table` stores column headers, parsed `text/template` templates, row data, footers, and customizable printer callbacks. `New()`, `AddColumn()`, `AddRow()`, `AddFooter()`, `Write()`, and helper `printLine()` form the API. Template funcmap exposes `join`.

Control flow: `Write()` renders templates for all rows, computes display widths across headers and cell lines using `ui.DisplayWidth`, prints a multi-line header, separator, each row, another separator, and optional footers. `printLine()` handles multi-line cells and column padding.

State and persistence: table contents are in-memory. `Write()` uses a reusable `bytes.Buffer` per cell and does not mutate rows.

Dependencies/integration: depends on `text/template`, `strings`, and UI width helpers for Unicode-aware alignment.

Risks: `AddColumn()` panics on bad templates by design. Custom printer callbacks must preserve newline semantics. Multiline and wide-character display depends on `ui.DisplayWidth`.

Test signals: `table_test.go` checks empty tables, spacing, multi-line headers/cells, footers, custom joins, and Unicode width effects.
