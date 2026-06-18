# File Research: sources/os/plan9/plan9/sys/src/cmd/cb/cbtype.c

Character classification table for `cb`. It defines `_cbtype_[]`, an ASCII table whose bit flags classify control, whitespace, punctuation, operator, digit, uppercase/lowercase, and hex characters.

The table backs the custom `isalpha`, `isdigit`, `isop`, and related macros in `cbtype.h`, avoiding dependency on libc ctype behavior inside the formatter.
