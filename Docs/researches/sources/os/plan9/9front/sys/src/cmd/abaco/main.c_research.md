# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/main.c

Abaco process entry point, display/webfs initialization, event threads, icon/color setup, and snarf support.

Key responsibilities:
- Parses options for initial column count, webfs mount point, charset, font, and stderr behavior.
- Opens webfs control, snarf device, display, mouse, keyboard, and plumber fds.
- Initializes icons, timers, fonts, global row/columns, and initial URL pages.
- Spawns keyboard and mouse event threads.
- Handles window resize, plumb messages, refresh channel, mouse buttons, and keyboard input.
- Implements snarf read/write helpers.

Important behavior:
- Uses `rfork(RFENVG|RFNAMEG)` to isolate environment/name space.
- Initial URLs are distributed up to `WPERCOL` per column.
- Keyboard input updates `activecol` except for scroll/navigation keys.
- Mouse thread locks the global row around hit dispatch.
- Large snarf buffers are not written to avoid rio truncation.

Dependencies:
- Uses Plan 9 draw/thread/plumb APIs, Abaco row/page/text command code, and webfs at `/mnt/web` by default.

Notable risks:
- `putsnarf()` writes chunks but formats from `rs->r` rather than `rs->r+i`, so repeated chunks would duplicate the beginning for large selections.
- Event threads depend on global mouse pointer state.
