# File Research: sources/os/bsd/openbsd-src/sbin/restore/extern.h

## Purpose

Cross-file function declarations for the restore program.

## Contents

Declares symbol table, directory, extraction, tape, utility, interactive, and remote tape functions used across `main.c`, `dirs.c`, `interactive.c`, `restore.c`, `symtab.c`, `tape.c`, `utilities.c`, and shared `dumprmt.c`.

## Notable Groups

- Tree/symbol operations: `addentry()`, `lookupino()`, `lookupname()`, `moveentry()`, `freeentry()`, `dumpsymtable()`, `initsymtable()`.
- Directory operations: `extractdirs()`, `treescan()`, `dirlookup()`, `pathsearch()`, `rst_opendir()`, `rst_readdir()`, `rst_closedir()`, `setdirmodes()`.
- Restore actions: `createfiles()`, `createleaves()`, `createlinks()`, `removeoldleaves()`, `removeoldnodes()`, `nodeupdates()`, `verifyfile()`.
- Tape/input operations: `setinput()`, `setup()`, `getfile()`, `getvol()`, `skipfile()`, `skipmaps()`, `newtapebuf()`.
- Remote tape operations are imported from `../dump/dumprmt.c`.
