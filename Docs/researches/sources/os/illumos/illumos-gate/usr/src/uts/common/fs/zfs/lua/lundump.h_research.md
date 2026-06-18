# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lundump.h

## Purpose

Declares Lua binary chunk dump/undump helpers and binary chunk header constants.

## APIs

- `luaU_undump`
- `luaU_header`
- `luaU_dump`

## Constants

- `LUAC_TAIL`: byte trailer used to detect conversion/corruption errors.
- `LUAC_HEADERSIZE`: expected binary header size.

## Risks And Notes

- Header size must remain consistent with both `luaU_header` and `LoadHeader` in `lundump.c`.
- `luaU_dump` is declared here but implemented elsewhere.
