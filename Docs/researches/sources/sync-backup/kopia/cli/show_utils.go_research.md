<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/show_utils.go -->
# sources/sync-backup/kopia/cli/show_utils.go

## Purpose
Collects formatting and display helpers for content output, human-readable units, timestamps, compression percentage, and multiline indentation.

## Important APIs, Types, And Functions
Key functions are `showContentWithFlags`, `maybeHumanReadableBytes`, `maybeHumanReadableCount`, `formatTimestamp`, `formatTimestampPrecise`, `convertTimezone`, `formatCompressionPercentage`, and `indentMultilineString`. Global `timeZone` controls timestamp conversion.

## Control Flow
`showContentWithFlags` optionally wraps input in a gzip reader, optionally buffers and JSON-indents content, then copies to the output writer. Formatting helpers are used across snapshot/list/report commands.

## State And Persistence Behavior
No repository state is changed. The global `timeZone` is process state and can affect all timestamp formatting.

## Dependencies And Integration Points
Depends on gzip, JSON indentation, internal copy and units helpers, and Go time locations.

## Risks And Edge Cases
JSON indentation buffers the entire stream, which is unsafe for very large objects. Invalid timezone names silently fall back to original timestamp. `timeZone` global is not concurrency-safe for tests changing it.

## Test Signals
Tests should cover gzip, JSON indentation errors, time zone modes, compression percentage edge cases, and human-readable toggles.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/show_utils.go -->
