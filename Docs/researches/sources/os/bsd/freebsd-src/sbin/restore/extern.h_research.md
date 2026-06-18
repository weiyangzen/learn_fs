# File Research: sources/os/bsd/freebsd-src/sbin/restore/extern.h

Purpose: shared function prototype header for the `restore` program.

Contents:
- Declares restore workflow entry points such as `setup()`, `extractdirs()`, `createfiles()`, `createleaves()`, `createlinks()`, `setdirmodes()`, and `checkrestore()`.
- Declares symbol-table APIs including `addentry()`, `lookupino()`, `lookupname()`, `moveentry()`, `freeentry()`, `dumpsymtable()`, and `initsymtable()`.
- Declares tape I/O APIs including `setinput()`, `getvol()`, `getfile()`, `skipfile()`, `skipmaps()`, `extractfile()`, and byte-swapping helpers.
- Defines `enum set_extattr_mode` for setting extended attributes by file path, symlink path, or file descriptor.
- Includes optional remote tape prototypes from `../dump/dumprmt.c`.

Integration: binds together the mostly global-state restore modules. This header makes the program’s cross-file coupling explicit: tape state, directory database, symbol table, utility functions, and high-level restore algorithms are all mutually visible.

Risk notes: APIs are C-era global-state oriented and lack const-correctness in several pathname parameters. Function contracts are mostly implicit in implementation comments rather than types.
