# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/fix_grouping.c

Read completely: 109 lines.

This file implements `__fix_locale_grouping_str`, converting textual locale grouping strings such as `3;3;-1` into POSIX grouping byte sequences. It edits the supplied string in place, skips semicolons, handles `-1` as `CHAR_MAX`, parses one- or two-digit group sizes, and returns a static no-grouping sequence for empty or invalid input.

Important interactions: used by locale category loaders to normalize numeric and monetary grouping fields from locale data files.

Security/reliability notes: the function casts away const and mutates the input buffer, so callers must pass writable storage unless they expect the static fallback. It assumes values are at most two decimal digits.
