# File Research: sources/os/bsd/netbsd-src/sys/sys/ttydefaults.h

Read completely: 115 lines.

Defines system-wide default terminal mode and control characters.

Key elements:
- Default flags set canonical echoing terminal behavior with input translation, output processing, signals, extensions, 8-bit chars, receiver enabled, and hangup-on-close.
- Default speed is `B9600`.
- Defines `CTRL(x)` and default control characters for EOF, EOL, erase, interrupt, status, kill, min/time, quit, suspend, start/stop, literal-next, discard, word erase, and reprint.
- Provides compatibility aliases such as `CEOT`, `CBRK`, `CRPRNT`, and `CFLUSH`.
- Kernel `TTYDEFCHARS` can instantiate the `ttydefchars[NCCS]` table; otherwise it declares it extern.

Risks and notes:
- Defaults shape first-open terminal behavior system-wide.
- Depends on `termios` constants being visible before inclusion.
