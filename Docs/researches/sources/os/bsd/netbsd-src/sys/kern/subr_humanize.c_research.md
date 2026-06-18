# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_humanize.c

Read completely: 117 lines.

Implements compact byte-count formatting. `humanize_number()` writes an integer value with optional SI or binary prefixes so the result fits the supplied buffer length, using decimal powers to decide when to scale by the divisor. It supports suffixes such as `"B"` and prefixes through exa.

`format_bytes()` wraps `humanize_number(..., "B", 1024)` and removes a trailing `" B"` for unscaled byte values.

Risks and notes:
- Returns `-1` for null buffers/suffixes or buffers too small for the minimal formatted value.
- Scaling uses integer division, so output is intentionally coarse rather than fractional.
- The binary-prefix mode still uses legacy `K/M/G...` prefix spelling rather than IEC `Ki/Mi`.
