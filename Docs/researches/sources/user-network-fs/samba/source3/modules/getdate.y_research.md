# sources/user-network-fs/samba/source3/modules/getdate.y

## Purpose
Authoritative Bison grammar and lexer source for Samba's imported GNU `get_date()` parser. It parses human-oriented absolute and relative time expressions into a `time_t`.

## APIs, Types, And Control Flow
The file defines `textint`, lexical `table`, meridian constants, and `struct parser_control`. Grammar rules recognize times (`10pm`, `10:30`, `10:30:05 -0500`), local and named zones, weekdays and ordinal weekdays, slash dates, ISO-style dates, month-name dates, compact numeric dates/times, and relative units with `ago`. After parsing, `get_date()` applies semantic checks, resolves two-digit years, uses `mktime`, handles explicit zones with `tm_gmtoff` or `tm_diff`, applies weekday offsets, and adds relative seconds with overflow detection.

## State, Dependencies, Integration
All parser state is call-local and reentrant through `%pure-parser`; no persistent data is written. Static lookup tables encode supported words, months, weekdays, time units, relative words, common zone abbreviations, and military zones. It depends on libc `localtime`, `gmtime`, `mktime`, ctype/string APIs, optional timezone fields, and Bison generation.

## Risks And Test Signals
The grammar intentionally has 13 shift/reduce conflicts, so rule changes can alter accepted parses. Ambiguous abbreviations and locale/DST behavior are host-sensitive. The word buffer truncates after 20 characters for lookup, and signed numeric accumulation can overflow before final checks. Test signals should cover every grammar family, duplicate component rejection, comments, plural units, military zones, local DST abbreviations, `ago` inversion, and regeneration equivalence against `getdate.c`.
