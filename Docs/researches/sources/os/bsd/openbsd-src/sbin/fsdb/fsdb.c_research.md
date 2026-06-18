# File Research: sources/os/bsd/openbsd-src/sbin/fsdb/fsdb.c

## Scope

Interactive FFS debugger shell. It opens an FFS filesystem using fsck setup code, exposes inode and directory mutation commands, and marks the filesystem dirty on exit.

## Main APIs And Commands

- `main()` parses `-f fsname` and `-d`, calls `setup(fsys, 1)`, enters `cmdloop()`, marks the superblock dirty, and finalizes.
- `cmdloop()` uses `libedit`/history and dispatches command table entries.
- Commands include `inode`, `lookup`/`cd`, `back`, `active`/`print`, `clri`, `uplink`, `downlink`, `linkcount`, `ls`, `rm`, `ln`, `chinum`, `chname`, `chtype`, `chmod`, `chown`, `chgrp`, `chlen`, `chflags`, `chgen`, `mtime`, `ctime`, `atime`, and quit aliases.

## Control Flow

The shell starts focused on `ROOTINO`. Command input is split by `crack()`, first offered to `el_parse()`, then matched against `cmds`. Inode focus commands load `curinode` through `ginode()`. Directory commands use `ckinode()` callbacks to list names, find components, change a slot inode, or change a slot name. Link/name commands delegate to fsck helpers `makeentry()` and `changeino()`.

Metadata mutators parse and validate values, update fields through `DIP_SET()`, call `inodirty()`, and print the updated inode. `dotime()` parses `YYYYMMDDHHMMSS[.nsec]` and uses `mktime()`.

## Dependencies

- Reuses `setup()`, `ckfini()`, `ginode()`, `clearinode()`, `ckinode()`, `findino()`, `makeentry()`, `changeino()`, and inode macros from fsck_ffs.
- Uses `libedit`/`history` for command editing.
- Shares many fsck globals locally because linked fsck modules expect them.

## Risks And Edge Cases

- The tool deliberately does low-level unchecked mutations; it always marks the filesystem dirty and tells the user to run fsck.
- Directory name replacement only succeeds if the new `DIRSIZ()` fits the existing record length.
- `chmode()` and several mutators return `1` even after successful modification, causing the loop to warn about nonzero return; this is existing behavior.
