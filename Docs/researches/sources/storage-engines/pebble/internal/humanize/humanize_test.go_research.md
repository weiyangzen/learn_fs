# sources/storage-engines/pebble/internal/humanize/humanize_test.go

## Purpose
`humanize_test.go` validates compact formatting for byte and count values against datadriven golden output.

## Important APIs, Types, And Functions
`TestHumanize` dispatches datadriven commands `bytes` and `count`, parses each input line as an `int64`, and writes `config.Int64` output.

## Control Flow
The test chooses `Bytes` or `Count` by command, iterates input rows using `crstrings.LinesSeq`, parses decimal integers, and appends one formatted line per input.

## State And Persistence Behavior
The persistent behavior contract lives in `testdata/humanize`. No runtime state persists.

## Dependencies And Integration Points
It uses `datadriven`, `crstrings`, `bytes.Buffer`, `strconv`, and `fmt`. It directly exercises package-level formatting configs.

## Risks And Edge Cases
The test only covers values present in the golden file. It does not explicitly test `Uint64`, redaction interface behavior, or overflow beyond suffix arrays.

## Test Signals
Passing datadriven output signals stable suffix choice, rounding, negative formatting, and byte/count base differences.
