# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lundump.c

## Purpose

Loads precompiled Lua binary chunks into runtime `Closure`/`Proto` structures.

## Main APIs

- `luaU_undump(lua_State *L, ZIO *Z, Mbuffer *buff, const char *name)`: loads one precompiled chunk from a `ZIO`.
- `luaU_header(lu_byte *h)`: constructs the expected binary chunk header for this build.

## Core Behavior

- Reads primitive values, vectors, strings, bytecode, constants, nested prototypes, upvalues, line info, local-variable debug info, and upvalue names.
- Validates all integer counts are non-negative.
- Validates the binary header against signature, Lua version, format, endianness, `sizeof(int)`, `sizeof(size_t)`, `sizeof(Instruction)`, `sizeof(lua_Number)`, and integral-number flag.
- Creates a top-level Lua closure, loads its prototype, and adjusts closure upvalue count if needed.
- Throws `LUA_ERRSYNTAX` on truncated, incompatible, or corrupted chunks.

## Dependencies

- Object/prototype allocation: `lfunc.h`, `lobject.h`.
- Protected error throwing: `ldo.h`.
- Memory and strings: `lmem.h`, `lstring.h`.
- Buffered input: `lzio.h`.

## Risks And Notes

- Binary chunks are not portable across builds with different integer sizes, instruction sizes, endianness, or `lua_Number` configuration.
- `LoadString` reads the serialized trailing NUL but interns/creates the string without it.
- `luai_verifycode` is empty unless configured; bytecode verification may be absent.
