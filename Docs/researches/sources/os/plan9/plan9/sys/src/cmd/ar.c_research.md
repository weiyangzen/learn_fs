# File Research: sources/os/plan9/plan9/sys/src/cmd/ar.c

Portable ASCII archive tool implementation.

Key points:
- Supports `r/u`, `d`, `x`, `t`, `p`, `m`, and `q` archive commands with option parsing for pivot insertion/move, verbose, update, create, local temp files, and timestamp preservation.
- Uses up to three logical temp files: archive start, moved/inserted middle, and archive end.
- Parses and writes portable `ar` headers through the `HEADER_IO` macro.
- Rebuilds archives through `install`, optionally generating `__.SYMDEF` when all members are compatible object files.
- `scanobj`, `objsym`, and `wrsym` collect text/data symbols using `mach` object readers.
- Temp-file subsystem stores member images in memory, spilling to disk if allocation fails.

Dependencies:
- Uses Plan 9 `bio`, `mach`, and `ar.h`.

Notable behavior:
- Duplicate text symbols prevent archive replacement when generating symbol definitions.
- GNU-produced trailing slashes in member names are stripped when reading headers.
