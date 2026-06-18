# File Research: sources/os/bsd/freebsd-src/sbin/restore/Makefile

Build file for the UFS dump restore utility.

Key elements:
- Builds `restore` from sources in sibling `dump` directory.
- Creates `rrestore` link and manpage alias.
- Source list includes `main.c`, `interactive.c`, `restore.c`, `dirs.c`, `symtab.c`, `tape.c`, `utilities.c`, and `dumprmt.c`.
- Adds `-DRRESTORE` and `-D_ACL_PRIVATE`; warning level is set to 2.

Dependencies:
- Uses `.PATH` to reuse dump/restore source files and `bsd.prog.mk`.
