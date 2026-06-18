# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strcasestr.c

Implements case-insensitive substring search. It lowercases the first needle character, scans the haystack for matching candidates, then uses `strncasecmp()` for the remainder.

An empty needle returns the original haystack pointer.
