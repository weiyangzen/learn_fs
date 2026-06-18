# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/main.c

## Scope

Command-line frontend and prompt implementation for `fsck_msdos`.

## Main APIs

- `main()` parses `-p`, `-y`, `-n`, and `-f`, validates a single filesystem argument, sets the canonical device name, and exits with `checkfilesys()`.
- `ask(def, fmt, ...)` implements interactive, preen, yes-to-all, no-to-all, and read-only prompt behavior.
- `usage()` reports syntax via `errexit()`.

## Control Flow

`-f` is accepted for consistency with `fsck_ffs` but ignored. `-n` enables `alwaysno`, `-y` enables `alwaysyes`, and `-p` enables preen. `ask()` auto-fixes default-yes repairs in preen mode unless read-only, prints yes/no for forced modes, and supports `F` to switch to yes-to-all during an interactive session.

## Dependencies

- Calls `checkroot()`, `setcdevname()`, `blockcheck()`, and `checkfilesys()`.
- Uses globals declared in `ext.h`.

## Risks And Edge Cases

- In read-only mode, `ask()` always answers no even when `alwaysyes` is set.
- Preen mode only performs repairs whose caller supplied `def=1`.
