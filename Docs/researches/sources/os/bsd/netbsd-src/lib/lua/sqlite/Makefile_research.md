# File Research: sources/os/bsd/netbsd-src/lib/lua/sqlite/Makefile

## Summary
Builds the Lua SQLite extension module.

## Main Responsibilities
- Defines `LUA_MODULES=sqlite`.
- Builds `sqlite.c`.
- Links against NetBSD’s external public-domain SQLite library.
- Includes `bsd.lua.mk`.

## Integration Notes
The module exposes SQLite database and statement APIs to Lua code.
