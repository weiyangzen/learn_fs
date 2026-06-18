# sources/storage-engines/pebble/metamorphic/history.go

## Purpose
`history.go` records operation results and Pebble log output for metamorphic runs, normalizes concurrent histories into operation order, and compares histories from different option configurations. It is the deterministic observation layer that turns random execution into comparable text.

## Important APIs, Types, and Functions
- `history` wraps a stdlib `log.Logger`, an atomic error slot, an optional failure regexp, and a mutex-protected closed bit.
- `newHistory`, `Close`, `Recordf`, `Infof`, `Errorf`, `Fatalf`, and `Error` implement recording plus Pebble logger behavior.
- `historyRecorder` binds a `history` to one operation index and exposes `Recordf` and `Error` to individual op `run` methods.
- `CompareHistories` reads all history files, strips comment lines, reorders by operation index, and returns the first differing run plus a focused diff.
- `reorderHistory`, `extractOp`, and `readHistory` implement the normalization pipeline for multi-threaded operation output.

## Control Flow and State
Operations record one non-comment line through `historyRecorder.Recordf`; `history.Recordf` appends a trailing `#<op>` marker so later diffs can identify the logical operation even after comments are stripped. Pebble logger methods write comment-prefixed timestamped lines that are ignored by `readHistory` during comparison.

The mutex serializes writes and rejects operation records after `Close`, while informational/error log calls after close are suppressed. `Fatalf` records a comment log and stores the first fatal error. `Recordf` scans formatted output against `failRE`; a match stores a failure error used by execution loops to stop.

## State and Persistence Behavior
The file itself writes to any `io.Writer` passed into `newHistory`; in normal runs this includes an on-disk `history` file and optionally stdout. The comparison logic reads persisted history files from run directories. It deliberately strips `//` comment logs to prevent nondeterministic logging noise from affecting metamorphic equality.

## Dependencies and Integration Points
`history` implements Pebble's logger interface and is installed by `RunOnce` in `meta.go`. Every op in `ops.go` records through `historyRecorder`. `CompareHistories` is used by `Compare` and `RunAndCompare` to identify divergent option configurations. The file uses `crstrings.LinesSeq`, Cockroach errors, `difflib.SplitLines`, and `testify/require` for file-read assertions.

## Risks and Edge Cases
- `Recordf` panics if the format string contains newlines, because each operation must map to one reorderable history line.
- `extractOp` assumes every non-comment history line contains a trailing `#<op>` marker.
- `reorderHistory` panics if an operation index exceeds the number of lines, which indicates incomplete output despite successful execution.
- Comment stripping means differences only visible in Pebble logger output are intentionally ignored unless they trigger `failRE` or fatal state.

## Test Signals
`history_test.go` verifies comment log formatting, failure regexp detection, and data-driven history reordering. `meta.go` exercises the comparison pipeline during full metamorphic runs.
