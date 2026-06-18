# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/cmd.h

## Purpose
Declares command return codes and interactive command handlers for `fdisk`.

## Key Contents
- Return/status codes:
  - `CMD_EXIT`
  - `CMD_QUIT`
  - `CMD_CONT`
  - `CMD_CLEAN`
  - `CMD_DIRTY`
- Prototypes for reinit, manual, edit, setpid, select, swap, print, write, exit, quit, abort, help, flag, and update commands.

## Notes
The command return codes drive the higher-level user edit loop in files outside this grouped subset.
