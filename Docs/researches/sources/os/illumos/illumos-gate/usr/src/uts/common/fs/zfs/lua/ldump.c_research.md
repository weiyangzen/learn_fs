# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldump.c

## Role

`ldump.c` serializes Lua function prototypes into precompiled binary chunks.

## Main Responsibilities

- Defines `DumpState` with Lua state, writer callback, callback data, strip flag, and status.
- Emits binary blocks, characters, integers, numbers, vectors, strings, bytecode, constants, nested prototypes, upvalue descriptors, and debug metadata.
- Omits source, line, local, and upvalue-name debug data when `strip` is set.
- Writes the Lua binary chunk header through `luaU_header`.
- Exposes `luaU_dump` for dumping a `Proto` through a `lua_Writer`.

## Integration Points

Used by `lua_dump` in `lapi.c`. The output format matches `lundump` expectations for loading binary chunks.

## Risk Notes

The writer callback runs with the Lua lock released and then reacquired. Dump format is tightly coupled to the exact `Proto`, `TValue`, opcode, and numeric representation of this build.
