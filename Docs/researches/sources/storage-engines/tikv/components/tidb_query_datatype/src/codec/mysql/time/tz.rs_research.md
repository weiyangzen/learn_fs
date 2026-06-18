# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/tz.rs

## Purpose
This file defines TiKV's unified time-zone wrapper for MySQL time handling. `Tz` abstracts over fixed offsets, IANA named zones from `chrono_tz`, and the host local time zone so the rest of the MySQL time module can operate through chrono's `TimeZone` trait.

## Important APIs, Types, and Functions
`Tz` has variants `Offset(FixedOffset)`, `Name(chrono_tz::Tz)`, and `Local(Local)`. Constructors are `from_offset(secs)`, `from_tz_name(name)`, `utc()`, and `local()`. `from_tz_name("system")` maps to local time. `get_chrono_tz` returns the named zone only when the variant is `Name`, which lets callers distinguish IANA zones from fixed/local zones.

`TzOffset` mirrors the selected zone result as `Local(FixedOffset)`, `Fixed(FixedOffset)`, or `NonFixed(<chrono_tz::Tz as TimeZone>::Offset)`. It implements chrono `Offset` by returning a fixed offset via `fix`.

## Control Flow and State
The `TimeZone for Tz` implementation delegates every chrono offset lookup and local/UTC construction method to the wrapped variant, then wraps the returned offset in the corresponding `TzOffset`. This preserves whether the source was local, fixed, or named while still allowing chrono `Date` and `DateTime` values to be produced with `Tz` as the zone type. Formatting uses debug-style output for fixed and named zones because those chrono types do not expose the desired `Display`.

## Dependencies and Integration Points
This module depends on `chrono` and `chrono_tz`. It is re-exported by `time/mod.rs` and used by `EvalConfig`/`EvalContext` consumers to parse, validate, pack, unpack, and display timestamp values. It is also used in tests to force UTC, fixed offsets, and named DST-aware zones such as `America/New_York`.

## Risks and Edge Cases
`from_offset` casts `i64` to `i32` before `FixedOffset::east_opt`, so callers should pass chrono-valid second offsets. `Local` depends on host environment settings, which can make behavior less reproducible than named or fixed zones. Named zones can produce ambiguous or nonexistent local times at DST boundaries; callers in `mod.rs` generally choose `earliest()` and convert failures to truncation.

## Test Signals
This file has no local tests, but it is exercised indirectly by the time module's timestamp parsing, timezone suffix conversion, local-time construction, packed timestamp codec, and DST arithmetic tests.
