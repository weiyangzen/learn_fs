# File Research: sources/os/plan9/9front/sys/src/cmd/acme/acme.c

This is Acme's main program: startup, global event threads, window layout initialization, plumbing integration, command-process tracking, font cache, icons, and snarf interaction.

Key responsibilities:
- `threadmain()` parses flags, initializes namespace bindings, fonts, draw/mouse/keyboard state, timers, regex, channels, plumbing, 9P file server, temp disk, row/columns/windows, and worker threads.
- `readfile()` creates an initial window and loads a named file or directory.
- `shutdown()` handles notes, dumps layout on non-kill exit, and terminates.
- `killprocs()` closes the file server, posts hangup to child commands, and removes the Acme error service.
- `acmeerrorinit()` exposes an error pipe through `/srv/acme.<user>.<pid>`.
- `plumbproc()` reads plumber messages from the `edit` port.
- `keyboardthread()` dispatches keyboard input to row/window text handling and delayed tag commit.
- `mousethread()` handles resize, plumbing, warning flushes, focus logging, selection, execute, look, scroll, drag, and chord behavior.
- `waitthread()` tracks child command start/exit, Kill requests, command names in the row tag, and error reporting.
- `xfidallocthread()` pools `Xfid` workers for the 9P file server.
- `newwindowthread()` lets the 9P server create windows from a graphics-safe thread.
- `rfget()`/`rfclose()` manage reference-counted fonts and the font cache.
- `iconinit()` builds tag/text colors and scroll/button images.
- `putsnarf()`/`getsnarf()` synchronize Acme's snarf buffer with `/dev/snarf`.

Important dependencies:
- Coordinates most modules in this group: row/column/window/text, fsys, exec, look, log, regex, disk, timer.
- Uses Plan 9 services: `/dev/snarf`, plumber ports, `/srv`, namespace bind, draw, keyboard, mouse, thread channels.

Filesystem/storage relevance:
- Starts Acme's synthetic 9P filesystem via `fsysinit()`.
- Creates a per-session temp disk through `diskinit()`.
- Reads initial files/directories and dumps/restores layout through row code.
- Exposes `/srv/acme.user.pid` for external error integration.

Notes:
- Child command lifecycle is asynchronous and robust against races where wait messages arrive before command registration.
- `mousethread()` logs `"focus"` events when active windows change, feeding the global `/mnt/acme/log` mechanism.
