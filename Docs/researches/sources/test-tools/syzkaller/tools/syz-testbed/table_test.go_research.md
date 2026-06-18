# sources/test-tools/syzkaller/tools/syz-testbed/table_test.go

## Purpose
This file tests relative value calculation for the `Table` abstraction used in syz-testbed stats displays.

## Important APIs, types, and functions
- `TestRelativeValues` constructs a two-column table with `ValueCell`s backed by `sample.Sample`, calls `SetRelativeValues("A")`, and asserts computed/omitted percent changes.
- Uses `testify/assert` for no-error and delta/nil assertions.

## Control flow
The test creates row1 with base A=2 and comparison B=3, row2 with only B=1, then verifies B in row1 receives about +50%, A receives no percent change, missing row2/A remains nil, and row2/B does not get a percent change because the base column is missing.

## State and persistence behavior
No files or persistent state. It mutates the in-memory table as production code would.

## Dependencies and integration points
Depends on local `NewTable`, `NewValueCell`, and `SetRelativeValues`, plus `pkg/stat/sample`. It is the direct regression test for the relative comparison behavior used by the HTML stats table.

## Risks and edge cases
Coverage is narrow: it does not assert p-values, wrong base cell types, outlier removal, zero base values, CSV rendering, footer aggregation, or panic behavior.

## Test signals
Strong for the basic percent-change path and missing-base guard. Remaining table behavior still needs separate coverage.
