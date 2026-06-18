# sources/test-tools/strace/src/string_to_uint.c

Purpose: shared decimal, non-negative integer parser for command-line and procfs-derived numeric strings.

Important APIs/types/functions: `string_to_uint_ex(str, endptr, max_val, accepted_ending)` wraps `strtoll` and validates non-empty input, conversion progress, non-negative value, upper bound, overflow, and optional accepted trailing delimiter.

Control flow: clear `errno`, parse base 10, reject empty/non-numeric/negative/out-of-range/ERANGE values, reject unexpected trailing characters, optionally return the parsed end pointer, and return the value as `long long` or `-1` on failure.

State and persistence behavior: only uses `errno`; no retained state.

Dependencies and integration points: used by inline wrappers in `string_to_uint.h` and by option parsing/PID parsing in `strace.c`.

Risks: `-1` is both error sentinel and outside accepted domain by design. Accepted-ending validation checks one character only, so callers must inspect `endptr` if more structure matters.

Test signals: empty input, whitespace, negative values, `LLONG_MAX` overflow, value over `max_val`, accepted `:` delimiter, rejected delimiter, and valid zero.
