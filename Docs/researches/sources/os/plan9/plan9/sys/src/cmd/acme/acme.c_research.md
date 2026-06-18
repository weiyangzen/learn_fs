# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/acme.c

This is Acme’s main program: initialization, event threads, plumber integration, process tracking, font cache, icon colors, and snarf bridge.

Key behavior:
- `threadmain()` parses flags, initializes environment, fonts, display, mouse/keyboard, timers, regex engine, channels, plumber fds, 9P filesystem service, disk backing store, rows/columns/windows, and worker threads.
- `mousethread()` is the main UI dispatcher for mouse input, resize, plumber messages, and queued warnings.
- `keyboardthread()` routes keyboard input to the row/window under the mouse or bart mode target, with delayed tag commit.
- `waitthread()` tracks external commands, updates the row tag command list, reports exits, and handles `Kill`.
- `xfidallocthread()` allocates/recycles `Xfid` workers for the Acme 9P filesystem.
- `newwindowthread()` allows the filesystem server to request a new GUI window without drawing from the server proc.
- `rfget()`/`rfclose()` maintain reference-counted font cache and default fixed/variable font state.
- `putsnarf()`/`getsnarf()` synchronize Acme’s internal snarf buffer with `/dev/snarf`.

Important details:
- Acme binds `/acme/bin` and `/acme/bin/$cputype` before `/bin`.
- Shutdown dumps the row layout unless killed/exited explicitly.
- `/srv/acme.$user.$pid` is created as an error service pointing at an internal pipe.
- External command lifecycle is coordinated through `Command` records and channels.

Filesystem relevance:
- Central: starts `fsysinit()`, creates the Acme 9P service, uses `/dev/snarf`, plumber ports, `/srv`, `/tmp`, and per-command process handling.
