# File Research: sources/os/plan9/plan9/sys/src/cmd/date.c

Small Plan 9 `date` command.

Key responsibilities:
- Parses flags:
  - `-n` prints numeric seconds since epoch.
  - `-u` prints UTC via `gmtime()`/`asctime()`.
- Optional single positional argument is parsed as seconds with `strtoul`.
- Without an argument, uses current `time(0)`.
- Default output uses local `ctime()`.

Research notes:
- If both `-n` and `-u` are supplied, numeric output wins because `nflg` is checked first.
