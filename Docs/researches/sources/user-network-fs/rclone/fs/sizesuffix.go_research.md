# sources/user-network-fs/rclone/fs/sizesuffix.go

## Purpose
This file defines `SizeSuffix`, an int64-backed size flag type that parses and formats binary size suffixes for rclone options and JSON.

## Important APIs, Types, and Functions
- `type SizeSuffix int64` and constants `Kibi` through `Exbi` define binary units.
- `String`, `ByteUnit`, `ByteRateUnit`, `BitUnit`, and `BitRateUnit` format values.
- `Set(s string) error` parses strings such as `1K`, `1MiB`, `102B`, bare numbers, and `off`.
- `Type` identifies the flag type as `SizeSuffix`.
- `Scan` implements `fmt.Scanner`.
- `SizeSuffixList` implements sorting.
- `UnmarshalJSONFlag` and `(*SizeSuffix).UnmarshalJSON` parse JSON strings or integers.

## Control Flow
Formatting chooses the largest binary unit below the value and emits either integer or three-decimal precision; negative values render as `off`. Parsing treats bare numeric values as KiB, `B`/`b` as bytes, `K/M/G/T/P/E` and `Ki`/`KiB` forms as binary units, rejects unknown suffixes and negative numeric values, and maps `off` to `-1`.

## State and Persistence
The type is pure value state with no global mutation or persistence.

## Dependencies and Integration Points
It depends on `encoding/json`, `fmt`, `math`, `sort`, `strconv`, and `strings`. `Option.String` and option parsing use it for size configuration values, and JSON config/RC paths can unmarshal it.

## Risks and Edge Cases
Bare numbers default to KiB rather than bytes, which is intentional but easy to misuse. `MB` decimal-style suffixes are rejected. Very large parsed floats are converted to `SizeSuffix` without explicit overflow checks in `Set`, despite max/min constants being declared.

## Test Signals
`sizesuffix_test.go` covers string/unit formatting through EiB, parser accepted/rejected suffixes, scanning, and JSON string/integer unmarshalling.
