# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/statusbar.c

Progress/status bar utility. It reads progress pairs from stdin and displays either a graphical Plan 9 window bar or a text-mode bar.

Input format:
- Lines tokenize into two fields: current numerator and denominator.
- Percentage is `n * 100 / d`.

Modes:
- Default graphical window using draw/event.
- `-t` text mode.
- `-k` disables killing the parent on delete/control-C.
- `-w minx,miny,maxx,maxy` sets new window rectangle.

Core behavior:
- `newwin()` creates a new rio/window-system window by mounting `$wsys` on `/mnt/wsys`, rebinding `/dev`, and redirecting stdio.
- `drawbar()` updates only changed bar regions in graphics mode and uses backspaces/delta output in text mode.
- A child process watches keyboard/mouse events and sends an interrupt note to the parent on delete/control-C unless `-k`.

Dependencies and integration:
- Uses Plan 9 draw, bio, and event libraries.
- Includes local copies of helper logic that comments say should be in a library.

Notable risks:
- `ptext` is assigned with `r.min.x+4` as y coordinate, likely a typo, though it is not otherwise used.
- `postnote(PNCTL, child, "kill")` is called even when `child == -1` in text mode.
- Window setup is deeply Plan 9 namespace/window-system specific.
