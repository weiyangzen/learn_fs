# File Research: sources/os/bsd/netbsd-src/lib/lua/bozohttpd/Makefile

## Summary
Builds the `bozohttpd` Lua module from the bozohttpd source tree.

## Main Responsibilities
- Defines `LUA_MODULES=bozohttpd`.
- Builds `glue.c` from the external bozohttpd Lua path.
- Links against `libbozohttpd`.
- Adds include path for the bozohttpd source tree.
- Includes `bsd.lua.mk`.

## Integration Notes
The actual module source is in `libexec/httpd/lua`, not this directory.
