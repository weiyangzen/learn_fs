# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lbitlib.c

## Role

`lbitlib.c` implements Lua's `bit32` library for fixed-width bitwise operations.

## Main Responsibilities

- Defines a 32-bit default bit width via `LUA_NBITS`.
- Implements `band`, `btest`, `bor`, `bxor`, `bnot`, logical shifts, arithmetic right shift, rotations, field extraction, and field replacement.
- Trims all results to the configured bit width.
- Validates bit field positions and widths before extraction/replacement.
- Registers the module through `luaopen_bit32`.

## Integration Points

The file uses only public Lua and auxiliary APIs for argument conversion and function registration.

## Risk Notes

Shift and rotate operations avoid undefined full-width shifts by checking bounds and masking counts. Field argument validation prevents access beyond `LUA_NBITS`.
