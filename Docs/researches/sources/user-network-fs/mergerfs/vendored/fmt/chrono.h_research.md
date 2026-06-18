# sources/user-network-fs/mergerfs/vendored/fmt/chrono.h

## Purpose

This fmt header adds formatting support for C and C++ chrono/time types. It covers safe duration conversion, `std::tm`, `std::chrono::duration`, system/UTC/local time points, and C++20 calendar types or local fallbacks.

## Important APIs, types, and functions

Public aliases include `fmt::sys_time`, `fmt::utc_time`, and `fmt::local_time`. `fmt::gmtime` converts `time_t` or `sys_time` to UTC `std::tm` using thread-safe platform functions when possible.

Formatter specializations cover `std::chrono::duration<Rep, Period>`, `std::tm`, `sys_time<Duration>`, `utc_time<Duration>`, `local_time<Duration>`, and calendar types `weekday`, `day`, `month`, `year`, and `year_month_day`.

Internal machinery includes `safe_duration_cast` helpers, `detail::duration_cast`, `parse_chrono_format`, `tm_format_checker`, `chrono_format_checker`, `tm_writer`, `duration_formatter`, `get_locale`, fractional-second helpers, unit-name mapping through `get_units`, and locale transcoding helpers for time strings.

## Control Flow

Duration conversion routes through checked integral and floating conversions when `FMT_SAFE_DURATION_CAST` is enabled. Overflow or unsupported range throws `format_error("cannot format duration")`.

Chrono format parsing requires `%`-style specifiers. `parse_chrono_format` scans text, handles padding modifiers `_` and `-`, dispatches date/time/duration/timezone callbacks, supports `E` and `O` alternative forms, and rejects unsupported specifiers. Checkers validate whether a format is legal for `std::tm` or a duration before formatting.

`tm_writer` formats calendar fields from a `std::tm`. It uses fast classic-locale paths for common fields and delegates to `std::time_put` when localized output is needed. `duration_formatter` maps a duration to days/hours/minutes/seconds/subseconds, handles negative values and NaN/Inf for floating reps, and supports `%Q` for value and `%q` for units.

Time-point formatters convert to `std::tm` using UTC conversion for `sys_time`, `utc_clock::to_sys` for `utc_time`, and a no-timezone `gmtime` interpretation for `local_time`. Subsecond adjustment handles negative fractional epochs.

## State and Persistence Behavior

Formatter instances retain parsed specs, dynamic width/precision references, locale flags, and the chrono format substring. Per-format calls allocate temporary memory buffers before applying outer width/alignment. `get_locale` conditionally placement-constructs a `std::locale` in a union and destroys it manually. No global mutable state is used except static classic locale and UTC string storage.

## Dependencies and Integration Points

It depends on `<chrono>`, `<ctime>`, `<locale>`, streams, math, algorithms, and fmt `format.h`. It integrates with standard C time APIs (`gmtime_r`, `gmtime_s`, `std::gmtime`), `std::time_put`, codecvt-based localized string conversion, C++20 chrono calendar/time-zone types when present, and fmt's base parser, buffers, locale references, and numeric writers.

## Risks and Edge Cases

Duration casts can overflow; safe mode reduces undefined behavior but mixed integer/floating casts still fall back to standard `duration_cast`. Locale paths depend on deprecated codecvt and platform library behavior. Timezone formatting for `std::tm` depends on non-standard `tm_gmtoff` and `tm_zone` members when present; otherwise UTC fallbacks are used. Durations intentionally lack date information, so date specifiers are rejected. Negative time points with subseconds require careful second borrowing. Floating durations need NaN/Inf handling and precision validation.

## Test Signals

Tests should cover `%Q`, `%q`, `%H:%M:%S`, fractional seconds, padding modifiers, locale `L`, invalid date specifiers for durations, timezone specifiers with and without `tm_gmtoff`, safe-cast overflow, negative durations and time points, NaN/Inf floating durations, C++20 calendar formatters, and platform-specific `gmtime_r`/`gmtime_s` fallbacks.
