# File Research: sources/os/plan9/plan9/sys/src/cmd/unicode.c

Read fully: 127 lines, 2079 bytes. SHA-256 prefix: `1df8a47aeab95c3c`.

This is a small Unicode conversion utility. Usage supports three modes:
- hex code points to UTF-8 characters,
- ranges `hexmin-hexmax` to code-point/character listings,
- `-n` or non-hex input to print numeric Unicode values for UTF-8 text.

Functions:
- `range()` parses and validates hex ranges, printing six-digit hex code points and `%C` characters in rows.
- `nums()` walks UTF-8 strings with `chartorune()`, validates genuine `Runeerror` encodings, and prints code points.
- `chars()` parses individual hex values and prints `%C`, with `-t` suppressing newlines for text output.

Integration: uses Plan 9 rune and Bio APIs.

Risk notes: range mode is selected when the first argument contains `-` and `-n` is not set; invalid input returns descriptive exit strings.
