# File Research: sources/os/plan9/plan9/sys/src/cmd/vt/vt.c

This file implements the VT100/ANSI/xterm-ish terminal parser and renderer.

Supported key tables:
- `vt100fk`, `ansifk`, `vt220fk`, and `xtermfk` map named keys and function keys to escape sequences.
- `vt220` mode is documented as mostly VT100 with different cursor key defaults.

Character-set handling:
- `gmap` maps DEC graphics characters to ASCII approximations.
- SO/SI switch between G1/G0 graphics state using `g0set`, `g1set`, and `isgraphics`.

Main parser:
- Handles control characters: bell, backspace, tab, linefeed/formfeed/vertical tab, carriage return, SO/SI, ignored controls, delete.
- Handles ESC commands: save/restore cursor, reset, index/next-line/reverse-index, tab set, identification, ANSI/keypad toggles, character set selection, OSC title setting, and many ignored VT features.
- CSI parsing accepts numeric operands separated by `;` or `?`.

CSI capabilities:
- Identification/status/cursor position reports.
- Tab clearing.
- Mode set/reset: linefeed mode, 80/132 columns, origin relative/absolute, wraparound, cursor visibility.
- Character attributes via `setattr`.
- Scroll region.
- Cursor movement up/down/right/left, absolute column/row, and home.
- Display/line erase.
- Delete/insert/erase chars.
- Insert/delete lines.
- Scroll up/down.

Rendering:
- Printable text is optionally mapped through graphics table, line-wrapped, batched, and drawn via `drawstring`.
- `setattr` maps SGR attributes and 8-color foreground/background values to shared image pointers.

Documented limitations:
- Does not handle cursor movement characters inside escape sequences.
- Tab stops beyond fixed table size are limited.
- Whole-screen reverse video ignored.
- ESC `#` double-width/double-height/confidence tests ignored.
- Cursor key sequences not affected by keypad application mode.
- VT52 and some rare features omitted.

Notable quirks:
- Debug `print` calls remain for reset and unknown escape cases, which can write into terminal output stream.
- Several DEC private mode branches are parsed by operand count rather than explicit `?` state.
