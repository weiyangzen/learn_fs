# File Research: sources/os/bsd/netbsd-src/lib/lua/syslog/Makefile

## Summary
Builds the Lua syslog extension module.

## Main Responsibilities
- Defines `LUA_MODULES=syslog`.
- Builds `syslog.c`.
- Includes `bsd.lua.mk`.

## Integration Notes
The module exposes libc syslog calls and constants to Lua.
