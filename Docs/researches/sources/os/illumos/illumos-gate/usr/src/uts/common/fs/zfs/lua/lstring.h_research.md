# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstring.h

## Purpose

Declares Lua string/userdata allocation and equality helpers plus string-size and interned-string macros.

## Key Definitions

- `sizestring`, `sizeudata`: allocation-size helpers.
- `luaS_newliteral`: literal string creation.
- `luaS_fix`: marks a string as fixed/non-collectable.
- `isreserved`: detects reserved-word short strings using `extra`.
- `eqshrstr`: short-string equality by pointer identity.

## APIs

- `luaS_hash`
- `luaS_eqlngstr`
- `luaS_eqstr`
- `luaS_resize`
- `luaS_newudata`
- `luaS_newlstr`
- `luaS_new`

## Risks And Notes

- `eqshrstr` depends on all short strings being interned.
- `isreserved` reuses the `extra` byte; code that mutates it must preserve lexer/metamethod assumptions.
