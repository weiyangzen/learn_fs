# sources/test-tools/syzkaller/tools/syz-testbed/table.go

## Purpose
This file provides the generic named-row/named-column table abstraction used by `syz-testbed` CSV and HTML reports, plus cell types for values, ratios, and booleans.

## Important APIs, types, and functions
- `Table` stores top-left header, ordered column headers, and a row/column cell map.
- `ValueCell` wraps a statistical sample, median value, optional percent change, and optional p-value.
- `RatioCell` and `BoolCell` provide displayable aggregate cells.
- Core methods include `NewTable`, `Get`, `Set`, `AddColumn`, `AddRow`, `SortedRows`, `ToStrings`, `SaveAsCsv`, `SetRelativeValues`, and `GetFooterValue`.

## Control flow
Tables preserve column insertion order while rows are sorted alphabetically on rendering. `SetRelativeValues` iterates rows, finds a base `ValueCell`, computes percent changes for other `ValueCell`s, removes outliers, and tries a U-test for p-values. Footer generation computes averages for homogeneous ratio/value columns or yes counts for boolean columns.

## State and persistence behavior
The table is in-memory until `SaveAsCsv` creates/truncates a CSV file. `SetRelativeValues` mutates existing `ValueCell` objects by filling `PercentChange` and `PValue` pointers.

## Dependencies and integration points
Uses `pkg/stat/sample` for medians, outlier removal, and U-test; `golang.org/x/exp/maps` plus `slices` for row sorting. HTML templates call table methods directly.

## Risks and edge cases
`AddRow` panics on length mismatch, which is acceptable for internal construction but not user input. `SortedRows` calls `maps.Keys(t.Cells)` and may need nil handling depending on library behavior, though `ToStrings` checks nil before calling it. `GetFooterValue` divides value averages by a count that is incremented as float; it returns a ratio over `len(t.Cells)` for bools, including rows with nil cells if any slipped through the homogeneous case.

## Test signals
`table_test.go` directly tests `SetRelativeValues` for a base column, percent change, nil base cells, and unchanged base cell extras. Additional tests should cover footer values, CSV output ordering, AddRow panic, and mixed cell columns.
