# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtquote.c

This file implements shell-style quoted string formatting.

Key behavior:
- `__quotesetup` scans byte or rune strings to decide if quoting is needed and compute output lengths.
- `qstrfmt` emits quoted strings with doubled quotes as needed.
- `quotestrfmt`, `quoterunestrfmt`, and `__quotestrfmt` provide formatter conversions.
- `quotefmtinstall` installs quote formatters.
- `__needsquotes` and `__runeneedsquotes` expose quote checks.

Important details:
- Handles byte and rune input/output variants.
- Supports sharp flag behavior for forced quoting.
