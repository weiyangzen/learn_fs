# File Research: sources/os/plan9/9front/sys/src/cmd/vt/main.c

Main UI, process, screen-buffer, input, selection, and event-loop implementation for the Plan 9 `vt` terminal emulator. It starts the child command under the synthetic console service from `fs.c` and drives the emulator core in `vt.c`.

Key behavior:
- `threadmain()` parses terminal mode options, initializes draw/mouse/keyboard state, allocates terminal colors, creates host I/O channels, starts `runcmd()`, and enters `emulate()`.
- `runcmd()` mounts the synthetic console, wires stdio to `/dev/cons`, assembles an optional rc command line, and execs `/bin/rc`.
- Maintains character, attribute, and color buffers for the visible screen plus a circular history buffer used by scrollback replay.
- `drawscreen()`, `drawcursor()`, `clear()`, `shift()`, and `scroll()` update display image regions from the screen buffers and mark changed lines.
- Input is split between cooked canonical line editing and raw terminal mode; raw mode maps special keys through function-key tables, while cooked mode handles erase, word kill, line kill, interrupt, newline, EOT, and local echo.
- `waitio()` multiplexes mouse, resize, keyboard, outgoing host input, and incoming host output channels.
- Window resize state is reflected through `WINCH`, `XPIXELS`, `YPIXELS`, `LINES`, `COLS`, and `TERM`; optionally sends interrupt when `consctl` enabled winch behavior.
- Selection supports swept text, word-like text, non-whitespace text, block selection, snarf buffer copy/paste, and plumber messages using OSC 7 current-directory context.
- Middle/right mouse menus expose scrollback, reset, paste, snarf, plumb, page mode, 24x80 geometry, newline toggles, raw/cooked mode, block selection, and exit.

Notable dependencies:
- Plan 9 graphics/event APIs: `draw`, `mouse`, `keyboard`, menus, images, `/dev/wctl`, `/dev/snarf`, plumber.
- Shared terminal emulator variables/functions from `cons.h` and `vt.c`.

Research notes:
- This is terminal UI and process plumbing, not general filesystem code.
- The `hc[0]`/`hc[1]` channel naming is from the emulator perspective: outgoing keyboard data to the host and incoming runes from the synthetic console.
- `drawscreen()` optimizes full-window upward scrolls through `scrolloff`, then redraws changed logical lines.
