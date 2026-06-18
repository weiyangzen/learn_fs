# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_time.rs

## Purpose

`impl_time.rs` implements TiDB/TiKV pushed-down scalar time, date, duration, interval, Unix timestamp, and parsing functions for the RPN expression engine. The functions are annotated with `#[rpn_fn]`, so `tidb_query_codegen` generates `*_fn_meta()` entries consumed by the crate-level dispatcher in `lib.rs`. The implementation is deliberately close to MySQL/TiDB semantics: it propagates SQL `NULL`, records warnings through `EvalContext`, respects SQL modes such as `NO_ZERO_DATE`, clamps MySQL `TIME` ranges, honors return field fractional-second precision, and converts invalid or overflowed values to either warnings plus `NULL` or hard errors depending on the context configuration.

This file has no storage-layer persistence. Its stateful behavior is evaluation-local: it reads `EvalContext` for timezone, SQL mode, statement flags, and warning/overflow policy; it reads `RpnFnCallExtra.ret_field_type` for return precision; and for interval functions it builds immutable per-expression metadata from the protobuf `Expr` tree.

## Important APIs, types, and functions

The basic date/time extractors and formatters include `date_format`, `date`, `sysdate_with_fsp`, `sysdate_without_fsp`, `week_with_mode`, `week_without_mode`, `week_day`, `day_of_week`, `day_of_year`, `week_of_year`, `year_week_with_mode`, `year_week_without_mode`, `to_days`, `to_seconds`, `month`, `month_name`, `hour`, `minute`, `second`, `time_to_sec`, `micro_second`, `year`, `day_of_month`, `day_name`, `period_add`, `period_diff`, `last_day`, and `quarter`. Most reject invalid zero dates by routing `Error::incorrect_datetime_value` through `ctx.handle_invalid_time_error`. `year` and `day_of_month` are special because a full zero date can return `0` unless `NO_ZERO_DATE` is active.

The time arithmetic surface includes `add_string_and_duration`, `sub_string_and_duration`, `date_diff`, `null_time_diff`, `add_datetime_and_duration`, `add_datetime_and_string`, `add_date_and_string`, `sub_duration_and_duration`, `sub_datetime_and_duration`, `sub_datetime_and_string`, `sub_duration_and_string`, `add_duration_and_duration`, `add_duration_and_string`, and the four `*_time_diff` variants. These functions parse `BytesRef` operands as `Duration` or `DateTime` as MySQL would, use checked arithmetic helpers from `tidb_query_datatype::codec::mysql`, and convert overflow to the configured invalid-time or overflow behavior. The `add_time_*_null` functions intentionally return `NULL` for unsupported `ADDTIME` result combinations registered in `lib.rs`.

`make_date` and `make_time` construct values from numeric parts. `make_date` applies MySQL's two-digit year conversion (`0..69` maps to `2000..2069`, `70..99` maps to `1970..1999`) and computes day-of-year against the proleptic calendar. `make_time` inspects argument field metadata through captured `args` to decide whether the hour argument is signed, validates minute/second ranges, clamps overflow to the MySQL maximum `838:59:59`, and uses `extra.ret_field_type.get_decimal()` as the result FSP.

The `ADDDATE`/`SUBDATE` interval family is centered on `AddSubDateMeta`, `build_add_sub_date_meta`, `AddSubDateConvertToTime`, `add_date`, `sub_date`, and the `add_sub_date_time_*` helpers. `build_add_sub_date_meta` validates the three-argument expression shape, extracts the interval unit literal from child 2, records whether the unit is a clock unit, and captures signedness/FSP details from the interval child field type. `AddSubDateConvertToTime` converts string, integer, real, decimal, and datetime operands into `Time`, changing the time type to `DateTime` for clock units and timestamps. The public generic wrappers cover all combinations of time operand type, interval operand type, and return type used by TiDB signatures, for example `add_date_time_string_interval_any_as_string`, `sub_date_time_datetime_interval_any_as_datetime`, and `add_date_time_duration_interval_any_as_duration`.

Unix timestamp support is implemented by `from_unixtime_1_arg`, `from_unixtime_2_arg`, `eval_from_unixtime`, `unix_timestamp_int`, `unix_timestamp_decimal`, `get_micro_timestamp`, `unix_timestamp_to_mysql_unix_timestamp`, and `find_zone_transition`. `eval_from_unixtime` accepts `Decimal` timestamps in the MySQL-supported range `0..=32536771199.999999`, splits integral and fractional parts, converts the fractional part to nanoseconds, and delegates to `DateTime::from_unixtime`. `get_micro_timestamp` builds a local `chrono` naive datetime, asks the configured TiDB timezone for the earliest mapped instant, and uses `find_zone_transition` for nonexistent local times at DST transitions. `unix_timestamp_to_mysql_unix_timestamp` returns `0` outside MySQL's supported timestamp range and truncates decimal output to the requested FSP.

`timestamp_diff` uses `build_timestamp_diff_meta` to parse and validate the interval unit literal before evaluation. Runtime evaluation rejects invalid zero endpoints and delegates to `DateTime::timestamp_diff`.

`str_to_date_date`, `str_to_date_datetime`, and `str_to_date_duration` call `Time::parse_from_string_with_format`, translate parse failure into truncation warnings plus `NULL`, enforce `NO_ZERO_DATE` for date/datetime return paths, and set the final type/FSP according to the signature and `RpnFnCallExtra`.

## Control flow and error handling

Most public functions follow the same RPN scalar pattern: accept nullable `Option` operands when the SQL function is nullable, return `Ok(None)` for `NULL` inputs, convert bytes with `from_utf8` or `std::str::from_utf8`, perform datatype parsing or arithmetic, and route domain errors through `EvalContext`. This is important because the same Rust error can be a warning plus `NULL` or a hard evaluation error depending on SQL mode and statement flags.

String plus/minus duration has a two-stage parse flow: first try exact `Duration`, then try `DateTime`, then issue an invalid datetime warning and return `NULL`. Datetime plus/minus string is stricter: parse the string as a `Duration`, return `NULL` on parse failure, then perform checked datetime arithmetic. Duration time-diff has additional clamping logic for results beyond MySQL `TIME` bounds but still representable within `i64` nanoseconds.

Interval add/sub wrappers use metadata captured at expression-build time rather than reparsing the interval unit for every row. Runtime control flow is: convert the time operand, convert the interval operand into an interval string using metadata signedness/decimal information, parse it into either an `Interval` or `Duration`, call the selected operation (`add_date`, `sub_date`, `Duration::checked_add`, or `Duration::checked_sub`), normalize FSP or string representation, and return the requested type. This structure is the main integration point between protobuf planning metadata and vectorized row evaluation.

Timezone conversion for `UNIX_TIMESTAMP` has a notable DST branch. If a local datetime maps to multiple instants, MySQL-compatible behavior selects the earliest. If it maps to no instant, the code binary-searches for the timezone transition within a 24-hour window and returns the transition instant. This creates a dependency on `chrono`, `chrono_tz`, and the configured `Tz`.

## State and persistence behavior

The file does not read or write durable state. All mutable state is scoped to evaluation:

- `EvalContext` accumulates warnings and provides SQL mode, timezone, and error policy.
- `RpnFnCallExtra` supplies return field metadata such as FSP.
- Generated `rpn_fn` metadata stores `AddSubDateMeta` or `IntervalUnit` as boxed per-expression metadata.
- Writer functions use `BytesWriter` and return `BytesGuard`, so string results are produced into the vectorized evaluation arena rather than persisted.

## Dependencies and integration points

The implementation depends heavily on `tidb_query_datatype::codec::mysql::{Time, Duration, Interval, IntervalUnit, WeekMode, Tz}` and associated conversion traits. It also uses `tidb_query_datatype::expr::{EvalContext, SqlMode}`, `FieldTypeAccessor`, `FieldTypeFlag`, `Decimal`, `Real`, `BytesRef`, `BytesWriter`, and `DateTime` aliases from the datatype codec. The `#[rpn_fn]` macro generates function metadata exported through this crate and selected by `lib.rs` for `tipb::ScalarFuncSig` variants.

The file integrates with `RpnExpressionBuilder` via metadata mappers (`build_add_sub_date_meta`, `build_timestamp_diff_meta`) and with vectorized execution through generated RPN stack adapters. Tests use `RpnFnScalarEvaluator`, `ExprDefBuilder`, and `LazyBatchColumnVec` to exercise both direct scalar evaluation and full expression-tree build/eval paths.

## Risks and edge cases

The highest-risk areas are MySQL compatibility and boundary behavior. Zero dates and incomplete dates are accepted by some functions and rejected by others. This is intentional but easy to regress if helpers are consolidated without preserving per-function SQL-mode semantics. Timezone behavior around DST gaps/overlaps is another sensitive path because it relies on `chrono_tz` mapping and a bounded binary search. Decimal timestamp conversion must preserve truncation and overflow behavior exactly, especially when multiplying fractional seconds to nanoseconds.

The interval family has a broad generic surface. A mismatch between a `ScalarFuncSig` mapping in `lib.rs`, its field types, and the generic wrapper selected here can produce wrong parsing rules or wrong return types. `make_time` depends on captured argument field signedness and return FSP; bugs here can appear only for unsigned hour operands or invalid FSP. Duration arithmetic intentionally clamps some out-of-range diffs to MySQL `TIME` extrema but treats i64 overflow as invalid; that distinction should remain explicit.

## Test signals

The in-file test module is broad. It covers formatting tokens, date extraction, all week modes, zero-date behavior, `TO_DAYS`/`TO_SECONDS`, string/duration addition and subtraction, `DATE_DIFF`, null-only signatures, date/datetime/duration arithmetic, `FROM_DAYS`, `MAKEDATE`, `MAKETIME`, month/day names and warning codes, period math, `LAST_DAY`, duration `TIMEDIFF` clamping, `QUARTER`, the large `ADDDATE`/`SUBDATE` signature matrix, `FROM_UNIXTIME`, `UNIX_TIMESTAMP` with offsets and named timezones, `TIMESTAMPDIFF`, and many `STR_TO_DATE` parsing patterns and failure cases. The tests are strong regression indicators for MySQL compatibility, but there is less explicit property coverage for arbitrary timezone databases, decimal edge overflow beyond listed cases, and future changes to interval-unit parsing.
