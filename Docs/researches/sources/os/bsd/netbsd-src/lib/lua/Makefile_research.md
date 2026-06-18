# File Research: sources/os/bsd/netbsd-src/lib/lua/Makefile

## Summary
Top-level build dispatcher for NetBSD Lua extension modules.

## Main Responsibilities
- Includes `bsd.own.mk`.
- Builds Lua subdirectories only when `${MKPIC} != "no"`.
- Adds `bozohttpd`, `gpio`, `libm`, `sqlite`, and `syslog` to `SUBDIR`.
- Includes `bsd.subdir.mk`.

## Integration Notes
The modules are skipped when PIC/shared-library support is disabled because Lua modules require dynamically loadable objects.
