# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lctype.h

## Role

`lctype.h` defines Lua-specific character classification macros for the lexer and numeric parser.

## Main Responsibilities

- Selects the internal fixed ASCII table when the platform encoding matches ASCII; otherwise falls back to standard C `ctype`.
- Defines Lua-specific predicates for alphabetic/alphanumeric characters, where `_` counts as alphabetic.
- Provides digit, whitespace, printable, hexadecimal, and lowercase conversion helpers.
- Declares `luai_ctype_` when using the internal table.

## Integration Points

Used by `llex.c` and `lobject.c` for source scanning, escape processing, and numeric conversion.

## Risk Notes

These macros do not exactly match standard `ctype.h`; they are tuned for Lua syntax and should not be reused as general-purpose locale-aware classification.
