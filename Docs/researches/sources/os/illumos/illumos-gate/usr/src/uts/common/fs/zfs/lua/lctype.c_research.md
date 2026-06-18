# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lctype.c

## Role

`lctype.c` provides Lua's internal character classification table when the build does not use the host C `ctype` library.

## Main Responsibilities

- Defines `luai_ctype_`, indexed with an extra leading entry so EOZ (`-1`) can be classified safely.
- Encodes alphabetic, digit, printable, space, and hexadecimal flags for ASCII input.
- Gives Lua fixed parser behavior independent of locale when `LUA_USE_CTYPE` is false.

## Integration Points

The lexer and object numeric parser use these classifications through `lctype.h` macros.

## Risk Notes

This table assumes ASCII when selected. Non-ASCII source text is not treated as identifier characters by this path.
