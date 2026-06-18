# File Research: sources/local-fs/xfsdump/librmt/Makefile

Builds `librmt.la`, the remote tape support library.

Key details:
- Includes top-level `include/builddefs`.
- Sets `LTLDFLAGS` empty to force a static-only libtool library build.
- Lists `rmtlib.h` and all `rmt*.c`/`isrmt.c` implementation files.
- Default target builds dependencies and library.
- `install` and `install-dev` depend on default but perform no extra install commands in this file.

Role:
- Packages the `/etc/rmt` protocol wrappers used by dump/restore tape I/O.
