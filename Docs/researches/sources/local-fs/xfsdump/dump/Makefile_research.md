# File Research: sources/local-fs/xfsdump/dump/Makefile

## Role

This makefile builds and installs the `xfsdump` executable from dump-local sources plus common and inventory sources.

## Source Organization

It links shared common headers/sources from `../common` and inventory headers/sources from `../inventory` into the dump build directory.

Source groups:

- `COMMINCL`: common headers used by dump.
- `INVINCL`: inventory headers.
- `INVCOMMON`: inventory implementation files.
- `COMMON`: common implementation files.
- `LOCALS`: dump-specific files such as `content.c`, `inomap.c`, and `var.c`.
- `LOCALINCL`: dump-specific headers.

## Build Settings

- Command target: `xfsdump`
- Local C files: dump-specific files
- Linked common C files: common and inventory implementation files
- Link libraries: UUID, handle, attr, remote tape, pthread
- `LCFLAGS = -DDUMP`

## Targets

`default` builds dependencies and the command.

`install` installs the command into the root sbin directory and also creates a symlink or second install in normal sbin when root sbin and sbin are distinct.

`install-dev` is empty.

The makefile also defines symlink rules for common and inventory files and includes generated dependencies from `.dep`.
