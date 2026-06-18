# sources/test-tools/fio/oslib/strsep.c

Purpose: fallback implementation of BSD/GNU `strsep()`.

Important APIs/functions: `strsep(char **stringp, const char *delim)` returns the next token, overwrites the delimiter with NUL, and advances `*stringp`.

Control flow and state: scans characters in the current string and compares each against all delimiter characters. When a delimiter or NUL is found, it updates `*stringp` to the next position or `NULL`.

Dependencies and integration: paired with `strsep.h`; used by fio parsing code, including zoned-device sysfs line trimming and profile option splitting.

Risks: modifies the input string. Empty tokens are returned, matching standard `strsep()` but differing from `strtok()` expectations.

Test signals: consecutive delimiters, empty input, no delimiter, delimiter at end, and `NULL` string pointer contents.
