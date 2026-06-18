# sources/sync-backup/git-lfs/tools/humanize/humanize.go

Purpose: parse and format byte sizes and byte rates for user-facing Git LFS progress/config output.

Important APIs/types/functions: constants `Byte` through `Pebibyte` and SI units, `ParseBytes`, `ParseByteUnit`, `FormatBytes`, `FormatBytesUnit`, `FormatByteRate`, and internal `log`.

Control flow: parsing scans the numeric prefix allowing digits, dot, and comma, parses it as float64, maps the suffix through `bytesTable`, multiplies, and rejects values at/above `math.MaxUint64`. Formatting chooses a base-1000 exponent, formats to one decimal for larger units, and rate formatting divides by duration with a one-nanosecond lower bound.

State and persistence: package-level unit tables only; no I/O or durable state.

Dependencies and integration points: used by `tq.Meter` for progress strings. Depends on `math`, `strconv`, `unicode`, Git LFS `errors` and `tr`.

Risks: parsing truncates fractional bytes when casting to `uint64`; rate formatting for zero duration intentionally clamps to nanosecond-scale and can produce very high rates; exponent indexes assume values remain within the defined `sizes` range.

Test signals: `humanize_test.go` covers many unit variants, rounding cases, unknown units, and byte-rate formatting.
