# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/unicode_letter.rs

## Purpose
Ports Go 1.21.3 Unicode case conversion logic so TiKV string functions match TiDB behavior.

## Important APIs, Types, And Functions
Constants identify upper, lower, and title case slots. `CASE_TABLE` stores sorted Unicode ranges and deltas. `to_case` performs range lookup and applies ordinary deltas or the `UPPER_LOWER` alternating-range rule. Public helpers are `unicode_to_upper`, `unicode_to_lower`, and `unicode_to_title`.

## Control Flow
ASCII is handled by direct arithmetic. Non-ASCII goes through binary search over `CASE_TABLE`; if a range matches, it applies the selected delta. For alternating upper/lower sequences, it clears or sets the low bit in the offset from the range start. If no range matches, the input char is returned unchanged.

## State And Persistence
Read-only static table only. No mutation or persisted state.

## Dependencies And Integration Points
Used by default `Encoding::lower`/`upper`, GBK, and GB18030. Its behavior is central to SQL `LOWER` and `UPPER` compatibility.

## Risks
The table is copied from a specific Go version, so future Unicode changes are intentionally not picked up unless regenerated. Invalid case indexes return replacement char internally. The `char::from_u32` return type forces callers to handle theoretically invalid mappings via `Option<char>`.

## Test Signals
Local `test_case` exercises ASCII, Latin-1, Turkish I, ligatures, Kelvin sign, and many table-driven mappings against expected case outputs.
