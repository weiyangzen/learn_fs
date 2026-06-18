# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltm.h

## Purpose

Defines Lua metamethod event enumeration and lookup macros.

## Key Definitions

- `TMS`: ordered metamethod IDs from `TM_INDEX` through `TM_CALL`.
- `gfasttm` / `fasttm`: quick metamethod lookup with cached absence flags.
- `ttypename`, `objtypename`: type-name lookup helpers.

## APIs

- `luaT_gettm`
- `luaT_gettmbyobj`
- `luaT_init`
- `luaT_typenames_`

## Risks And Notes

- Enum order is shared with arithmetic opcode constants and event-name arrays; changing it requires coordinated changes across the VM and object code.
- Only events up to `TM_EQ` use fast absence caching.
