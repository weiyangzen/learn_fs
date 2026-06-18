# File Research: sources/os/plan9/plan9/sys/src/cmd/vt/main.c

This file provides the generic window, input, history, menus, drawing, and host I/O substrate for the terminal emulator. It calls `emulate()`, which is implemented by either `vt.c` or `hp.c`.

Initialization:
- Parses terminal mode options:
  - `-2` VT220 key table.
  - `-a` ANSI key table.
  - `-b` black background.
  - `-c` disables color.
  - `-f` font.
  - `-l` log file.
  - `-x` xterm key table.
- Allocates host input buffer, initializes draw window, starts host event source via `ebegin`, initializes menus, colors, font metrics, and default colors.
- Exports `XPIXELS`, `YPIXELS`, `LINES`, `COLS`, and `TERM`.

Screen behavior:
- `newline` scrolls within `yscrmin..yscrmax` and supports page mode blocking.
- `scroll` copies screen rectangles and clears the vacated line.
- `bigscroll` scrolls up about one third of the screen for local scrollback behavior.
- `resize` recomputes character grid and clears screen.
- `setdim` requests a `/dev/wctl` resize for fixed rows/cols.

Input behavior:
- `waitchar` multiplexes resize, mouse menus, snarf playback, host data, keyboard events, and cursor display.
- In raw mode, keyboard special keys are mapped through current `funckey` table; newline and carriage return are translated.
- In cooked mode, `canon` implements backspace, line kill, word kill, interrupt, quit/newline, EOT, and local echo buffering.
- `sendnchars2` writes to the hosted shell fd.

Menus:
- Button 3 menu toggles 24x80, CR/NL translations, raw/cooked mode, and exit.
- Button 2 menu handles backup, forward, reset, clear, send snarf buffer, and page/scroll mode.

History:
- `hist[HISTSIZ]` stores received chars in a circular buffer.
- `backup` locates older content by line count and replays through `backp`.

Drawing:
- `curson` saves current cell background and draws a red/border cursor.
- `cursoff` restores cursor background.
- `drawstring` applies reverse and high-intensity color behavior and paints text.

Notable risks:
- `sendnchars` writes `p[n+1] = 0`, which assumes writable space beyond the transmitted buffer and can be unsafe for arbitrary caller buffers.
- Fixed-size buffers for echo/send impose practical typeahead limits.
