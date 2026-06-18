# File Research: sources/os/bsd/openbsd-src/sbin/fsdb/fsdb.h

## Scope

Shared declarations for the `fsdb` interactive debugger.

## Main Contents

- Declares imported low-level I/O and prompt functions: `bread()`, `bwrite()`, `reply()`.
- Defines `struct cmdtable` for command name, help text, argument bounds, and handler.
- Exposes active inode globals `curinode` and `curinum`.
- Declares utility functions `crack()`, `argcount()`, `printstat()`, `checkactive()`, `checkactivedir()`, and `printactive()`.

## Dependencies

Included by `fsdb.c` and `fsdbutil.c`; relies on `union dinode` and `ino_t` definitions from included UFS headers in users.

## Risks And Edge Cases

The command table stores `minargc`/`maxargc` including the command word itself; help and validation code report user argument counts as minus one.
