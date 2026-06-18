# File Research: sources/os/bsd/freebsd-src/sbin/fsdb/fsdb.c

## Purpose

Implements the interactive `fsdb` shell for inspecting and editing UFS/FFS filesystems.

## Main Flow

- `main()` parses `-d`, `-f`, and `-r`, opens and sets up the filesystem through fsck/libufs routines, then enters `cmdloop()`.
- On exit, critical modifications mark the filesystem dirty and warn the user to run fsck.
- Non-critical modifications leave clean state unchanged.

## Command Framework

`struct cmdtable cmds[]` maps command names to handler functions, argument counts, help text, and write-risk flags:
- `FL_RO`: read-only
- `FL_WR`: non-critical metadata write
- `FL_CWR`: critical filesystem-integrity write
- `FL_ST`: re-split final argument for names with spaces

Commands include:
- Navigation/inspection: `inode`, `lookup`, `cd`, `back`, `active`, `print`, `blocks`, `ls`, `findblk`
- Directory edits: `rm`, `del`, `ln`, `chinum`, `chname`
- Inode edits: `clri`, `uplink`, `downlink`, `linkcount`, `chtype`, `chmod`, `chown`, `chgrp`, `chflags`, `chgen`, `chsize`, `chdb`
- Time edits: `btime`, `mtime`, `ctime`, `atime`
- Exit: `quit`, `q`, `exit`, `quitclean`

## Important Logic

- `cmdloop()` uses libedit/history, parses commands, enforces read-only mode for write commands, and tracks whether modifications were critical.
- `setcurinode()` releases the prior inode and loads a new current inode.
- `focusname()` walks path components using fsck’s `findino()` and `ckinode()`.
- `findblk()` scans cylinder groups, inodes, direct blocks, and indirect trees to find owners of disk blocks.
- Directory slot functions (`chinumfunc()`, `chnamefunc()`) mutate directory entries through fsck directory traversal callbacks.
- Inode mutation handlers use `DIP_SET()` and `inodirty()` to write fields.

## Integration Points

Uses `fsck.h` globals and routines such as `sblock_init()`, `openfilesys()`, `readsb()`, `setup()`, `ginode()`, `irelse()`, `ckinode()`, `makeentry()`, `changeino()`, `clearinode()`, `inodirty()`, `cglookup()`, and `ckfini()`.

## Risk Notes

This is a direct metadata editor. Critical edits intentionally dirty the filesystem to force a later full fsck. `quitclean` can override that, warning the user that a modified filesystem is being marked clean.
