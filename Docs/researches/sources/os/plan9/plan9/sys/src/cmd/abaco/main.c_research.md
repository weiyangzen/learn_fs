# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/main.c

Abaco program entry point, UI initialization, event threads, plumbing, and snarf integration.

Key responsibilities:
- Parses options for charset, webfs mount point, and stderr handling.
- Initializes draw, mouse, keyboard, colors, fonts, icons, timers, channels, and the top-level row.
- Starts mouse, keyboard, plumbing, and refresh/event processing threads.
- Loads initial pages into columns.
- Handles shutdown notices.
- Processes plumb messages into browser look/open actions.
- Dispatches keyboard and mouse events to the selected text/page/window/row objects.
- Provides snarf buffer read/write helpers using Plan 9 `/dev/snarf`.

Dependencies:
- Uses Plan 9 thread, draw, mouse, keyboard, regexp, plumb, and html libraries.
- Coordinates every Abaco subsystem through globals from `dat.h`.

Notable risks:
- UI state is global and event-thread driven.
- Startup depends on the webfs mount point being present and usable.
