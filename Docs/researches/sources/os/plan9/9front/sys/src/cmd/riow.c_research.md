# File Research: sources/os/plan9/9front/sys/src/cmd/riow.c

`riow.c` is a keyboard-driven rio window controller and virtual desktop helper. It reads keyboard messages from stdin, filters Mod4-based shortcuts, writes unhandled key events to stdout, and controls rio through `/dev/wsys/*/wctl`.

It models windows as `W` records with rio ID, rectangle, virtual desktop number, flags for visible/current/sticky/fullscreen, and a forced-sticky bit. `wsupdate` enumerates `/dev/wsys`, reads each window's `wctl`, preserves prior virtual desktop metadata, detects current/visible status, and marks sticky windows by label.

Supported actions include spawning a new `window`, toggling fullscreen by saving/restoring geometry, toggling sticky, deleting the current window, moving/resizing with arrow keys, directional window cycling, switching desktops, and moving the current window to another desktop.

Desktop switching hides visible non-sticky windows from the old desktop, unhides windows assigned to the target desktop, restores the remembered current window per desktop, tops/current-marks it, and writes the active desktop number to fd 3.

`process` parses raw `/dev/kbd` messages, tracks modifier state from `k`/`K` events, applies shortcuts only when Mod4 is held, and preserves non-consumed key messages exactly enough for downstream consumers.
