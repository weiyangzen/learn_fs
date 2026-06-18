# File Research: sources/local-fs/xfsprogs/db/command.c

Purpose: central command registry and dispatcher for `xfs_db`.

Key behavior:
- Maintains global `cmdtab` and `ncmds`.
- `add_command` appends a `cmdinfo_t` and keeps the table sorted by command name with `qsort`.
- `find_command` searches by primary name or alternate name.
- `command` validates argument counts against `argmin`/`argmax`, resets platform getopt state, and calls the command handler.
- `init_commands` initializes all built-in command modules, including address, AG headers, attr, block, bmap, check, convert, crc, debug, echo, frag, freesp, fsmap, help, hash, inode, IO, log, metadump, output, print, quit, realtime, sb, type, write, dquot, fuzz, timelimit, iunlink, bmapinflate, and rdump modules.

Interactions:
- Every command module provides an init function that calls `add_command`.
- Uses `dbprintf` for user-visible command errors.
- Uses `platform_getoptreset` before dispatch so command-local option parsing starts cleanly.

Risks/notes:
- Duplicate command names are not rejected; sorted linear lookup returns the first matching entry.
- Command metadata controls help, stack-push capability, and argument validation.
