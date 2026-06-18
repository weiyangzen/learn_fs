# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/Makefile

## Scope

Standalone makefile for building the libc compatibility library component.

## Behavior

- Includes the parent libc `Makefile.inc`.
- Sets `LIB=cold`.
- Adds libc include and architecture include paths.
- Includes common compatibility subdirectory fragments for db, gen, locale, net, rpc, stdio, stdlib, and sys.
- Sets `COMPATARCHDIR` and `.PATH` for architecture-specific gen/sys sources.
- Finishes with `<bsd.lib.mk>`.

## Dependencies And Invariants

- Depends on NetBSD make variables `.CURDIR`, `ARCHSUBDIR`, `COMPATDIR`, and the compatibility subdirectory layout.
