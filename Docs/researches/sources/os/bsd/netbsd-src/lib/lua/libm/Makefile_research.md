# File Research: sources/os/bsd/netbsd-src/lib/lua/libm/Makefile

## Summary
Builds the Lua `libm` extension module.

## Main Responsibilities
- Defines `LUA_MODULES=libm`.
- Builds `libm.c`.
- Links against NetBSD `libm`.
- Includes `bsd.lua.mk`.

## Integration Notes
The module exposes C math library functions and constants to Lua.
