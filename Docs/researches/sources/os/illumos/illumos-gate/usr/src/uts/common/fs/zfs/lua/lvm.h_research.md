# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lvm.h

## Purpose

Declares Lua VM helper functions and common conversion/equality macros.

## Key Macros

- `tostring(L,o)`: true if already string or convertible number.
- `tonumber(o,n)`: true if already number or parseable string.
- `equalobj(L,o1,o2)`: raw tag equality plus Lua equality.
- `luaV_rawequalobj`: equality without metamethods.

## APIs

- Equality/comparison helpers.
- Numeric/string conversion helpers.
- Table get/set helpers.
- VM execution and yield-finish helpers.
- Concatenation, arithmetic, and length helpers.

## Risks And Notes

- `tonumber` mutates its first macro argument when conversion succeeds; callers must pass an assignable expression.
- `luaV_rawequalobj` passes `NULL` as state, suppressing metamethod equality.
