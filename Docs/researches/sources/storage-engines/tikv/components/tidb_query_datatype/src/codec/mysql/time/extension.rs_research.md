# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/extension.rs

Purpose: adds MySQL/TiDB date and weekday helper methods to `chrono::Weekday` and internal `Time`.

Important APIs/types/functions: `WeekdayExtension::{name, name_abbr}`, `DateTimeExtension::{days, calc_year_week, calc_year_week_by_week_mode, week, year_week, abbr_day_of_month, day_number, second_number}`, plus private `calc_day_number`, `calc_days_in_year`, and `calc_weekday`.

Control flow: weekday methods map enum variants to full or abbreviated English names. Week calculations implement TiDB/MySQL week-mode behavior by deriving day numbers, first weekday, year-boundary adjustments, and week numbering. `week` returns 0 for zero month/day. `year_week` forces year behavior. Day/second number helpers compute days or seconds since MySQL's zero date baseline.

State and persistence: no persistent state. All calculations are pure over a `Time` value and `WeekMode`.

Dependencies and integration points: depends on `chrono::Weekday`, internal `Time`, and `weekmode::WeekMode`. Used by SQL date formatting/extraction functions.

Risks: week numbering has many boundary conditions around January, ISO-like modes, Sunday/Monday starts, zero dates, and leap years. Private helpers are not directly tested in this file, so coverage is likely indirect through time function tests elsewhere.
