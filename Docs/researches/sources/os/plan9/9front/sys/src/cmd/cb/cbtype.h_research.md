# File Research: sources/os/plan9/9front/sys/src/cmd/cb/cbtype.h

Purpose: Declares `_cbtype_` and defines character classification macros for `cb`.

Key points:
- Defines bit flags `_U`, `_L`, `_N`, `_S`, `_P`, `_C`, `_X`, and `_O`.
- Defines macros for `isop`, `isalpha`, `isdigit`, `isspace`, `ispunct`, `isalnum`, and related functions.
- Defines simple ASCII `toupper`, `tolower`, and `toascii`.

Dependencies and interactions:
- Included by `cb.c` and `cbtype.c`.
- Requires `_cbtype_` from `cbtype.c`.

Research notes:
- Macros index `(_cbtype_+1)[c]`, so callers must pass valid ASCII-range values.
