# sources/sync-backup/bup/lib/bup/cmd/help.py

## Purpose
`help.py` dispatches to the top-level bup help or the system `man` command for a specific bup manual page.

## APIs and Control Flow
`main(argv)` parses exactly zero or one command argument. With no argument it `execvp`s `bup -h`. With one argument it builds `bup` or `bup-<command>`, checks for development manual pages under `../../Documentation`, temporarily sets `MANPATH` when present, and `execvp`s `man`. More than one argument is a fatal parse error.

## State, Dependencies, Integration, Risks, Tests
It replaces the process with `bup` or `man`, so there is no normal return on success. It mutates `os.environb['MANPATH']` only for the child exec path. Dependencies are `bup.path.exe`, `bup.path.exedir`, `glob`, and `argv_bytes`. Risks include missing `man`, stale development documentation paths, and command names that do not map to manuals. Test signals include no-arg exec target, one-arg docname construction, `MANPATH` injection when local manpage exists, and `EXIT_FAILURE` on `OSError`.
