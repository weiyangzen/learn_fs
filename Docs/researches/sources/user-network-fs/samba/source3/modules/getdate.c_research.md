# sources/user-network-fs/samba/source3/modules/getdate.c

## Purpose
Generated GNU Bison C output for the natural-language date parser defined by `getdate.y`. Samba keeps this generated artifact so consumers can build without regenerating the grammar. Its public result is `get_date(const char *p, const time_t *now)`, which converts absolute or relative date text into a `time_t`.

## APIs, Types, And Control Flow
The file embeds Bison parser tables, `YYSTYPE`, `yyparse(struct parser_control *)`, generated stack growth and error recovery code, plus copied semantic actions from `getdate.y`. Runtime flow is: initialize `parser_control` from `now` or `time(0)`, call `yyparse`, reject duplicate date/time/day/zone components, normalize year/month/day through `mktime`, optionally adjust for explicit time zones, then add relative hours/minutes/seconds with overflow checks. `yylex` recognizes signed and unsigned numbers, words, comments in parentheses, punctuation, meridians, months, weekdays, units, relative words, and zone names.

## State, Dependencies, Integration
All parse state is per-call in `parser_control`; there is no persistent storage. It depends on libc time APIs, optional `tm_gmtoff`, optional `tzname`, and the generated Bison skeleton. It integrates with `vfs_readonly.c`, which uses `get_date()` to parse configured readonly time windows.

## Risks And Test Signals
Risks include divergence from `getdate.y` if regenerated with a different Bison version, ambiguous timezone abbreviations, host-dependent DST handling, integer overflow in numeric lexing before later guards, and localtime/mktime boundary behavior. Useful tests parse absolute dates, ISO dates, `now`, `yesterday`, ordinal weekdays, numeric zones, DST local zone names, invalid duplicate clauses, and `time_t` boundary cases.
