# File Research: sources/os/bsd/freebsd-src/sys/sys/ttydefaults.h

System-wide default terminal settings header.

Key responsibilities:
- Defines default input, output, local, control flags, and default speed for first TTY open.
- Defines `CTRL(x)` control-character conversion and default control characters for EOF, EOL, erase, interrupt, status, kill, quit, suspend, start/stop, literal-next, discard, word erase, reprint, min, and time.
- Provides compatibility aliases for old control-character names.
- When `TTYDEFCHARS` is defined, emits the `ttydefchars[]` array in NCCS order and statically asserts its size.

Dependencies:
- Uses termios flag and control-character constants; the optional array includes `sys/cdefs.h` and `_termios`.

Notable risks:
- The header intentionally treats lowercase letters as uppercase in `CTRL(x)` despite strict control-character conversion expectations.
- `ttydefchars[]` ordering must remain synchronized with `NCCS` and termios control index definitions.
