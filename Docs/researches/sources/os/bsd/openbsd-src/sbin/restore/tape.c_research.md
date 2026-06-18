# File Research: sources/os/bsd/openbsd-src/sbin/restore/tape.c

This file is the dump-tape input and extraction engine for OpenBSD `restore`. It opens local, pipe, or remote tape input, validates dump headers, manages volume changes, reads records, extracts file payloads, and converts old dump header formats.

Key APIs:
- `setinput()`, `newtapebuf()`, `setup()`: configure input, allocate tape buffers, verify the dump, read inode maps, and initialize `usedinomap`/`dumpmap`.
- `getvol()`: prompts for and validates the next dump volume, including date and volume checks.
- `extractfile()`: dispatches extraction by inode mode for directories, symlinks, regular files, FIFOs, special files, sockets, and dry-run mode.
- `getfile()`, `skipfile()`, `skipmaps()`: consume dump block maps, pass allocated data to fill callbacks, and sparse holes to skip callbacks.
- `readtape()`, `findtapeblksize()`, `gethead()`: read physical tape records, handle short reads, EOF, resynchronization, checksums, byte swapping, and old-header conversion.

Behavior and integration:
- Maintains global tape state: `mt`, `pipein`, `blkcnt`, `numtrec`, `tapebuf`, `volno`, `curfile`, `spcl`, and dump timing metadata.
- Uses `setjmp`/`longjmp` around active file extraction so media changes or end-of-input can resume safely.
- Supports `RRESTORE` remote tape hooks, `-b` fixed blocking, auto block-size detection, multi-dump tape skipping, and pipe terminal fallback.
- Converts legacy `u_ospcl` headers into current `struct s_spcl` and normalizes old inode uid/gid fields.
- Preserves ownership, mode, flags, access/modify times, and birthtime where present.

Risk notes:
- Much of the file depends on global mutable extraction state, so control flow is hard to reason about around EOF, read errors, and volume transitions.
- `tapesread` uses bit shifts by volume number, which is only meaningful for small volume numbers despite accepting larger input.
- Symlink extraction accumulates with string operations over block data and relies on dump contents being well-formed NUL-terminated path data.
