# File Research: sources/os/plan9/9front/sys/src/cmd/cb/cbtype.c

Purpose: Defines the ASCII character classification table for `cb`.

Key points:
- `_cbtype_[]` maps characters to bit flags for uppercase, lowercase, numeric, space, punctuation, control, hex digit, and operator.
- Table is sized for ASCII plus leading sentinel offset behavior.

Dependencies and interactions:
- Included through `cbtype.h` macros such as `isop`, `isalpha`, `isdigit`, and `isspace`.
- Used by `cb.c` instead of libc ctype functions.

Research notes:
- This local ctype table gives `cb` deterministic ASCII classification independent of locale or libc behavior.
