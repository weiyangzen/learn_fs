# sources/storage-engines/pebble/internal/humanize/humanize.go

## Purpose
`humanize.go` formats byte and count values into compact human-readable strings that are considered redaction-safe.

## Important APIs, Types, And Functions
`config` stores a numeric base and suffix list. Package variables `Bytes` and `Count` configure IEC-like byte formatting and SI count formatting. `Int64` and `Uint64` format signed/unsigned values. `FormattedString` implements `fmt.Stringer` and `redact.SafeValue`. Helpers `logn` and `humanate` choose suffixes and one-decimal formatting.

## Control Flow
Values below 10 use the base suffix directly. Larger values compute an exponent from logarithms, scale and round to one decimal, and suppress decimals when the rounded value is at least 10. Negative signed values are formatted with a leading minus.

## State And Persistence Behavior
All configuration is immutable package state. No persistence or caching is involved.

## Dependencies And Integration Points
It depends on `fmt`, `math`, and Cockroach `redact`. It is used wherever Pebble logs or displays compact sizes/counts and wants redaction-safe markers.

## Risks And Edge Cases
The suffix arrays cap at exabytes/exa; values beyond the highest suffix can index past the suffix list. Rounding can produce boundary-looking values, such as `1023KB` vs `1.0MB`, based on the exponent chosen before rounding.

## Test Signals
`humanize_test.go` uses datadriven input to verify bytes/count formatting across representative values, including signed values.
