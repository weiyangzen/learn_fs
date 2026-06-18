# File Research: sources/local-fs/xfsprogs/db/help.c

## Purpose
Implements the `help` / `?` command for listing registered xfs_db commands and printing command-specific help.

## Main Interfaces
- Registers `help` through `help_init()`.
- `help_f()` either prints all command one-liners or looks up one named command.

## Control Flow
`help_all()` iterates `cmdtab[0..ncmds)` and prints each command name, alias, arguments, and one-line summary. `help_onecmd()` prints the one-line form and invokes the command's `help` callback when available.

## Dependencies
Uses command table globals and `find_command()` from the xfs_db command subsystem plus `dbprintf()` output.

## Risks And Invariants
Help output reflects only commands registered for the current mode; expert-only commands absent from `cmdtab` are not shown.
