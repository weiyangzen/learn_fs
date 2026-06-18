# File Research: sources/os/bsd/netbsd-src/lib/lua/Makefile.inc

## Summary
Common make include for Lua modules.

## Main Responsibilities
- Sets default `WARNS?=4`.

## Integration Notes
Submodule Makefiles inherit this warning level unless they override it.
