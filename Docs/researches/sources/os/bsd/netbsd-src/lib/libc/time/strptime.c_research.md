# File Research: sources/os/bsd/netbsd-src/lib/libc/time/strptime.c

## Purpose
Implements NetBSD libc `strptime` and `strptime_l`: parsing formatted date/time text into a caller-provided `struct tm`, with locale-aware names, numeric fields, recursive composite formats, epoch seconds, week-derived dates, and timezone parsing.

## Public Entry Points
- `strptime(const char *buf, const char *fmt, struct tm *tm)`: delegates to `strptime_l` with the current locale.
- `strptime_l(const char *buf, const char *fmt, struct tm *tm, locale_t loc)`: main parser.

The file defines weak aliases for both functions when supported.

## Parser State
The parser tracks which fields have been supplied using flags:
- `S_YEAR`, `S_MON`, `S_YDAY`, `S_MDAY`, `S_WDAY`, `S_HOUR`.

This lets it derive missing fields after parsing, such as day-of-year from month/day or month/day from ordinal day.

It also tracks split-century parsing for `%C` plus `%y`, week offsets from `%U`/`%W`, alternative modifiers `%E`/`%O`, and timezone offset sign.

## Supported Conversions
Composite conversions recurse through locale or fixed subformats:
- `%c`, `%D`, `%F`, `%R`, `%r`, `%T`, `%X`, `%x`.

Elementary conversions include:
- Weekday/month names: `%A`, `%a`, `%B`, `%b`, `%h`.
- Year and century: `%C`, `%Y`, `%y`.
- Date/time fields: `%d`, `%e`, `%H`, `%k`, `%I`, `%l`, `%j`, `%M`, `%m`, `%p`, `%S`.
- Epoch seconds: `%s`, parsed as nonnegative `time_t` and converted with `localtime_r`.
- Week fields: `%U`, `%W`, `%w`, `%u`.
- ISO week/year placeholders: `%g`, `%G`, `%V` are parsed or skipped but not fully resolved into dates.
- Timezone: `%Z` and `%z`.
- Whitespace/literals: `%n`, `%t`, `%%`.

## Timezone Parsing
For `%Z`/`%z`, the parser recognizes:
- `Z`, `UTC`, `UT`, `GMT`.
- Numeric ISO 8601/RFC 3339 offsets: `+hh`, `+hhmm`, `+hh:mm`, and negative variants.
- RFC 822/RFC 2822 North American abbreviations: `EST`/`EDT`, `CST`/`CDT`, `MST`/`MDT`, `PST`/`PDT`.
- Nautical/military single-letter zones except `J`, with `J` treated as local time.
- Current `tzname` values after `tzset`.
- Named zones loaded via `tzalloc` in `fromzone`.

When possible, it fills `tm_gmtoff`, `tm_zone`, and `tm_isdst`. Some loaded or military zones intentionally set `tm_zone = NULL`.

## Post-Parse Derivation
After format processing:
- If year plus month/day are known but yday is missing, calculates `tm_yday`.
- If year plus `%U`/`%W` week information are available, derives `tm_yday`, defaulting weekday to the week base when needed.
- If year plus yday are available but month or day-of-month is missing, derives them from `start_of_month`.
- If weekday is missing, derives `tm_wday`.

## Helpers
- `conv_num`: parses bounded unsigned decimal fields, where the upper limit controls digit count.
- `find_string`: case-insensitively matches full and abbreviated locale strings.
- `first_wday_of`: computes the first weekday of a Gregorian year.
- `fromzone`: loads a named timezone through `tzalloc` and extracts an offset/name signal.

## Notable Risks and Edge Cases
- `%G`, `%g`, and `%V` are not fully used to synthesize ISO week dates.
- `%s` accepts only nonnegative epoch seconds and checks overflow against `time_t`.
- `%Z` is permissive and may leave timezone fields partially specified.
- Recursive composite parsing calls `strptime`, not `strptime_l`, so nested locale handling depends on current-locale behavior.
