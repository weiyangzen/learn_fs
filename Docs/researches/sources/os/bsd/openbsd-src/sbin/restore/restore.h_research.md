# File Research: sources/os/bsd/openbsd-src/sbin/restore/restore.h

## Purpose

Shared global declarations, data structures, flags, and macros for the restore program.

## Key Definitions

Declares global option flags, inode maps, tape/dump metadata, command mode, terminal and temp directory state, old-format/byte-swap flags, and `__progname`.

Defines `struct entry`, the in-memory restore symbol table node. Entries track current name, type, flags, old inode number, checkpoint index, parent, sibling, hard-link chain, directory children, and inode hash chain.

Defines entry types `LEAF`, `NODE`, and synthetic `LINK`, flags such as `EXTRACT`, `NEW`, `KEEP`, `REMOVED`, `TMPNAME`, and `EXISTED`, link kinds, temp-name prefix, current tape-file context `curfile`, and actions `USING`, `SKIP`, and `UNKNOWN`.

Also declares `RST_DIR`, `FORCE` for directory mode restoration, inode bitmap macros `TSTINO`/`SETINO`, debug/verbose print macros, and `GOOD`/`FAIL`.

## Coupling

Every restore implementation file shares these globals and entry semantics. The symbol table, directory traversal, extraction scheduling, and tape reader all coordinate through `curfile`, inode maps, and `struct entry` flags.
