# File Research: sources/os/plan9/9front/sys/src/cmd/vt/vt.c

ANSI/VT100-style terminal emulator state machine used by `vt/main.c`. It parses input runes from `nextchar()`, handles control characters and escape sequences, updates cursor/screen state through callbacks in `main.c`, and emits terminal replies through `sendnchars()`.

Key behavior:
- Defines ANSI, VT220, xterm, and application cursor-key sequence tables plus DEC special graphics mapping.
- `emulate()` is the main parser loop, handling printable text batching, wrapping, G0/G1 graphics selection, ESC commands, CSI commands, and OSC commands.
- Supports cursor save/restore, reset, index/next-line/reverse-index, tab stops, cursor reports, terminal identification, scroll regions, line/character insertion and deletion, screen/line erase, cursor visibility, origin mode, auto-wrap mode, bracketed paste mode, and 80/132-column resize requests.
- `setattr()` implements common SGR attributes: reset, high intensity, underline, blink, reverse, invisible, and 8-color foreground/background state.
- `cursctl()` handles bell, backspace, tab, line feed, vertical/form feed, and carriage return, including raw-mode newline toggles.
- `osc()` supports title/label updates through `/dev/label` and OSC 7 working-directory capture, converting `file://host/path` into Plan 9 `/n/host/path` form and cleaning it.

Notable dependencies:
- Terminal buffer and drawing primitives from `main.c`: `clear`, `scroll`, `setdim`, `newline`, `drawstring`, `sendnchars`, `host_avail`, `rewound`.
- Plan 9 rune/ctype and path helpers.

Research notes:
- The file begins with explicit known limitations: incomplete cursor movement inside escape sequences, tab stops beyond the fixed array, reverse-video screen mode, double-width/height lines, VT220 fidelity, VT52 mode, and keypad mode behavior.
- OSC parsing intentionally ignores normal cursor-control effects inside OSC payloads via `cursctl()`.
