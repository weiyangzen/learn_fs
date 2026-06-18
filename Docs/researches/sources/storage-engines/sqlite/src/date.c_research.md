# sources/storage-engines/sqlite/src/date.c

## Purpose

`date.c` implements SQLite's date and time SQL functions. The full implementation registers `julianday`, `unixepoch`, `date`, `time`, `datetime`, `strftime`, `timediff`, current-time functions, and debug-only `datedebug`. When `SQLITE_OMIT_DATETIME_FUNCS` is set, it retains minimal `current_time`, `current_date`, and `current_timestamp` support for default column expressions.

## Important APIs, Types, and Functions

- `DateTime` caches a timestamp as Julian-day milliseconds (`iJD`), calendar fields (`Y/M/D`), time fields (`h/m/s`), timezone offset, and validity flags (`validJD`, `validYMD`, `validHMS`, `rawS`, `useSubsec`, `isUtc`, `isLocal`, `isError`).
- Parsing helpers include `getDigits()`, `parseTimezone()`, `parseHhMmSs()`, `parseYyyyMmDd()`, `parseDateOrTime()`, and `setRawDateNumber()`.
- Conversion helpers include `computeJD()`, `computeYMD()`, `computeHMS()`, `computeYMD_HMS()`, `validJulianDay()`, `computeFloor()`, `autoAdjustDate()`, and `clearYMD_HMS_TZ()`.
- Local time helpers `osLocaltime()` and `toLocaltime()` wrap platform `localtime` APIs and test fault injection.
- `parseModifier()` applies modifiers such as `unixepoch`, `julianday`, `auto`, `localtime`, `utc`, `weekday N`, `start of ...`, `floor`, `ceiling`, `subsec`, relative units, and signed date/time offsets.
- Output functions are `juliandayFunc()`, `unixepochFunc()`, `datetimeFunc()`, `timeFunc()`, `dateFunc()`, `strftimeFunc()`, `timediffFunc()`, and current-time wrappers.
- `sqlite3RegisterDateTimeFunctions()` inserts the function definitions into SQLite's built-in function table.

## Control Flow and Behavior

All full date/time functions route through `isDate()`. With no arguments, it uses the statement current time if the function is not being evaluated in a pure context. Numeric inputs become `rawS`, meaning they may later be interpreted as Julian day, Unix epoch seconds, or auto-detected. Text inputs are parsed as ISO-like date/time, time-only, `now`, numeric strings, or `subsec`/`subsecond` current time. Each modifier is then applied in order, and the final value is normalized to a valid Julian day.

`computeJD()` converts YMD/HMS/timezone data to Julian-day milliseconds and clears local calendar fields if timezone adjustment occurs. `computeYMD()` and `computeHMS()` lazily compute reverse views. The validity flags are central: modifiers clear stale representations after changing `iJD` or calendar fields so later functions recompute from the authoritative form.

Relative month/year additions are calendar-aware. They update Y/M, compute day overflow in `nFloor`, and allow `floor` to roll back to the last valid day or `ceiling` to keep default rollover. Numeric unit transforms convert seconds/minutes/hours/days directly in milliseconds, while month/year fractional remainders use fixed 30-day/365-day constants.

`strftimeFunc()` builds output using `sqlite3_str` under the connection length limit and supports SQLite-specific substitutions like `%f`, `%J`, `%G`, `%g`, `%k`, `%l`, `%P`, `%R`, `%T`, `%u`, `%U`, `%V`, and `%W`. Unknown format substitutions abort with NULL. `timediffFunc()` computes a signed calendar interval that can be used as a modifier to transform the second argument into the first.

## State and Persistence

No database pages are persisted. The main persistent-like state is statement-stable current time from `sqlite3StmtCurrentTime()`, ensuring multiple current-time calls in one statement agree. Localtime conversion uses process/OS timezone state and SQLite global fault-injection hooks in test builds. The registered built-ins become global function definitions via `sqlite3InsertBuiltinFuncs()`.

## Dependencies and Integration Points

This file depends on `sqliteInt.h`, C time APIs, SQLite value/result APIs, function purity checks, statement current-time plumbing, string accumulators, connection limits, mutexes around unsafe localtime variants, global test configuration, and the built-in function registration macros (`PURE_DATE`, `DFUNCTION`, `STR_FUNCTION`). It integrates with SQL execution as scalar functions and with default-value handling through the minimal omit build.

## Risks and Edge Cases

Range handling is strict: representable calendar dates are effectively `0000-01-01` through `9999-12-31 23:59:59.999`, and out-of-range `iJD` values return NULL. `rawS` is deliberately ambiguous until a modifier resolves it; wrong modifier order makes results NULL. Localtime outside 1970-2038 maps the year into an equivalent range, which is approximate and platform dependent. Fractional seconds are truncated around sub-millisecond input to avoid rounding surprises. Month/year arithmetic and `floor`/`ceiling` behavior are subtle around leap days and short months. Pure-function contexts must not observe current time or local timezone.

## Test Signals

Tests should cover ISO date/time parsing, timezone offsets and `Z`, negative years, date normalization like `2023-02-31`, Julian-day and Unix-epoch numeric interpretation, `auto` thresholds, modifier-order failures, `floor` and `ceiling` after month/year adds, `weekday`, `start of day/month/year`, `localtime`/`utc` conversions including injected failures, subsecond output for `datetime`, `time`, `unixepoch`, and `strftime('%s')`, week/year format specifiers, `timediff` invariants, length-limit failures in `strftime`, pure-function restrictions on `now`, and omit-datetime fallback current functions.
