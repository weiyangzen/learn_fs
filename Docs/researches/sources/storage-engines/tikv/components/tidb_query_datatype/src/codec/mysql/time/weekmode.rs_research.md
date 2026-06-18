# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/weekmode.rs

## Purpose
This small file defines MySQL week-mode flags used by date formatting and week/year-week calculations.

## Important APIs, Types, and Functions
`WeekMode` is a `bitflags` type with `BEHAVIOR_MONDAY_FIRST`, `BEHAVIOR_YEAR`, and `BEHAVIOR_FIRST_WEEKDAY`. `to_normalized` applies MySQL normalization: when Monday-first is not set, `BEHAVIOR_FIRST_WEEKDAY` is toggled. This mirrors the behavior used by TiDB/MySQL week calculations where mode bits are not interpreted independently.

## Control Flow and State
There is no persisted state. `to_normalized` copies the flag value, conditionally XORs the first-weekday bit, and returns the adjusted flag set.

## Dependencies and Integration Points
The only direct dependency is `bitflags`. The type is re-exported by `time/mod.rs` and used by time extension/date-format logic for `%U`, `%u`, `%V`, `%v`, `%X`, and `%x` formatting, plus public week/year-week APIs defined in the time extension module.

## Risks and Edge Cases
The main risk is semantic compatibility: changing the normalization rule would alter MySQL-compatible week numbering. Since the file itself has no tests, coverage is indirect through date-format and week calculation tests in the time module and extension module.

## Test Signals
No local test module exists. `time/mod.rs` date-format tests exercise week-related format tokens using `WeekMode::from_bits_truncate` values.
