# File Research: sources/os/plan9/9front/sys/src/cmd/kbmap.c

Graphical Plan 9 keyboard map selector. It enumerates keyboard map files from `/sys/lib/kbmap` unless explicit files are passed, lays them out as clickable rectangles, and writes the selected map into `/dev/kbmap`. The UI uses `draw`/`event` primitives, two blue image fills for normal/current state, and mouse button 3 release-on-same-item selection semantics.

`writemap` copies map files to `/dev/kbmap` without writing partial lines, buffering until a newline is available. `geometry`, `redraw`, and `eresized` keep the map grid responsive to window size. Keyboard input only handles quit (`q` or delete). This is a user-facing wrapper around the kernel keyboard map device, not a filesystem component.
