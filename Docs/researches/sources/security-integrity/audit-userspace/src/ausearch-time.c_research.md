## sources/security-integrity/audit-userspace/src/ausearch-time.c

Purpose: parses absolute and relative time expressions for `ausearch`/`aureport` start and end filters.

Important APIs/functions: `lookup_time()`, `ausearch_time_start()`, and `ausearch_time_end()`. Internal setters handle `now`, `recent`, `this-hour`, `boot`, `today`, `yesterday`, `this-week`, `week-ago`, `this-month`, and `this-year`; helpers clear/replace `struct tm` fields.

Control flow: option parsing passes date/time strings. Date keywords fill a `struct tm`; otherwise localized `strptime("%x")` parses dates and `strptime("%X")` parses times, adding seconds when only hour/minute is provided. `boot` reads `/proc/uptime`. Results are converted with `mktime()` into global `start_time` or `end_time`.

State/persistence: defines global `time_t start_time` and `end_time`; no persistence. Uses current local time and locale-sensitive date/time parsing.

Dependencies/integration: consumed by `ausearch-options.c`, `ausearch-common.h`, `ausearch-lol.c` filtering, `ausearch-match.c`, and `aureport.c`.

Risks/test signals: locale-sensitive `%x/%X` means CLI date format varies. DST handling is partly acknowledged by comments. End time for `today` special-cases current time; start `today` uses midnight. Tests should freeze time where possible and cover every keyword, boot failure, invalid years before 2004, partial time, DST boundaries, and start/end inclusivity.
