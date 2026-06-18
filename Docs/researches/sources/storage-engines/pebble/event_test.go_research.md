# sources/storage-engines/pebble/event_test.go

## Purpose
Tests `DataCorruptionInfo.FormatBlockDataAsHex`, the helper that renders captured corrupt block bytes for diagnostic logs.

## Important APIs, Types, And Functions
`TestFormatBlockDataAsHex` uses datadriven input. It strips whitespace from hex input, decodes bytes, constructs `DataCorruptionInfo{CorruptedBlockData: data}`, and returns `FormatBlockDataAsHex`.

## Control Flow
Each `format` command feeds arbitrary hex into the formatter. Invalid hex fails the test. The formatter behavior under empty input, grouping, offsets, line breaks, and truncation is captured in `testdata/format_block_data_as_hex`.

## State And Persistence Behavior
No DB state or files are used. The test is pure data formatting.

## Dependencies And Integration Points
Depends on `encoding/hex`, `strings`, `datadriven`, and the event payload defined in `event.go`. It supports corruption logging tests by keeping hex output stable.

## Risks And Edge Cases
The key edge cases are empty data, non-multiple-of-line-size data, 8-byte grouping, 64-byte rows, and the maximum dump limit. Since corruption diagnostics may be copied into logs, stable formatting matters for operational debugging.

## Test Signals
The datadriven output is the signal: exact byte offsets and hex group layout must match expectations.
