# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dmmain.c

This is a Macintosh Classic/Carbon example wrapper for running Ghostscript through the shared-library API with the `display` device. It was contributed by Nigel Hathaway and uses Metrowerks CodeWarrior SIOUX for command-line console behavior.

Key responsibilities:
- Initializes the Mac operating environment, SIOUX console, AppleEvent quit handler, cursor/event state, and scrollbar callback.
- Creates a Ghostscript instance with `gsapi_new_instance`, configures stdio, polling, and display callbacks, then runs normal Ghostscript startup via `gsapi_init_with_args` and `gsapi_run_string("systemdict /start get exec\n")`.
- Forces `-sDEVICE=display` and injects `-dDisplayFormat=<display_format>` into the command-line arguments.
- Implements Ghostscript stdio callbacks: `gsdll_stdin`, `gsdll_stdout`, and `gsdll_stderr`.
- Implements cooperative polling with `gsdll_poll`, forwarding pending Mac events into the local event loop.
- Implements `display_callback` functions for open, preclose, close, presize, size, sync, page, and update events.
- Maintains a linked list of `IMAGE` records, each binding a Ghostscript display handle/device pair to a Mac `WindowRef`, scrollbars, `PixMapHandle`, and update timing state.

Display behavior:
- Uses `DISPLAY_COLORS_RGB | DISPLAY_UNUSED_FIRST | DISPLAY_DEPTH_8 | DISPLAY_BIGENDIAN | DISPLAY_TOPFIRST`.
- `display_presize` rejects incompatible display formats.
- `display_size` binds Ghostscript's raster pointer directly into a QuickDraw `PixMap`, checks the QuickDraw row-byte limit, and refreshes scrollbars/window invalidation.
- `display_sync`, `display_page`, and `display_update` invalidate or throttle window redraws and process events.
- `doUpdateWindow` paints the current PixMap into the visible window area, with scrollbar offsets and gray fill outside the image bounds.

UI/event behavior:
- `get_input` works around SIOUX modal input by collecting console text through an event loop and returning buffered line data to Ghostscript.
- `window_create`, `window_invalidate`, and `window_adjust_scrollbars` manage Carbon/Classic window and scrollbar state.
- `doEvents`, `doMouseDown`, `doUpdate`, `doOSEvent`, `doInContent`, and `actionFunctionScroll` handle menus, dragging, resizing, zooming, update events, OS suspend/resume, and scrollbar tracking.
- `quitAppEventHandler` marks the global quit flag when the application receives a valid quit AppleEvent.

Notable implementation details and risks:
- This is highly platform-specific historical Mac code, dependent on Carbon, QuickDraw, SIOUX, and CodeWarrior target macros.
- It assumes a 32-bit-style QuickDraw PixMap layout and explicitly rejects rasters too large for QuickDraw row-byte encoding.
- The display memory is owned by Ghostscript; this wrapper only points QuickDraw at it.
- The code uses global process state (`gDone`, `instance`, `first_image`, SIOUX globals) rather than an isolated application object.
- It contains old C idioms such as assignment in conditions and minimal error recovery, appropriate to its historical sample-wrapper role.

Filesystem relevance:
- This file does not implement filesystem behavior.
- It only reads command-line arguments and delegates Ghostscript input/output through stdio callbacks.
- Its relevance is as a platform wrapper in the 9front-vendored Ghostscript tree.

Research classification: historical Mac Classic/Carbon Ghostscript shared-library display wrapper and event-loop integration.
