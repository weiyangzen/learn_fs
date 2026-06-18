# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lzio.c

## Purpose

Implements Lua buffered input streams and reusable parser/loader buffers.

## Main APIs

- `luaZ_init`: initializes a `ZIO` from a Lua reader callback and user data.
- `luaZ_fill`: obtains the next reader buffer and returns the first byte.
- `luaZ_read`: reads an exact byte count or returns missing byte count at EOF.
- `luaZ_openspace`: ensures an `Mbuffer` has at least the requested size.

## Core Behavior

- `luaZ_fill` unlocks the Lua state while calling the external reader, then relocks it.
- `luaZ_read` copies from buffered chunks and refills as needed.
- `luaZ_openspace` grows buffers to at least `LUA_MINBUFFER`.

## Dependencies

- Memory resizing macros from `lmem.h`.
- State locking macros from `lstate.h`/`lua.h`.

## Risks And Notes

- Reader callbacks must keep returned buffers valid until consumed.
- `luaZ_read` returns the remaining unread byte count, not a conventional success/failure boolean.
