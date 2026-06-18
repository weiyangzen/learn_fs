# File Research: sources/os/bsd/netbsd-src/lib/lua/gpio/Makefile

## Summary
Builds the Lua GPIO extension module.

## Main Responsibilities
- Defines `LUA_MODULES=gpio`.
- Builds `gpio.c`.
- Includes `bsd.lua.mk`.

## Integration Notes
The module exposes NetBSD GPIO ioctls to Lua.
