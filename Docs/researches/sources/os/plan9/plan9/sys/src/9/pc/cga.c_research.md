# File Research: sources/os/plan9/plan9/sys/src/9/pc/cga.c

PC CGA/VGA text-mode console output.

Key responsibilities:
- Defines text colors, screen geometry, attributes, and CGA base address.
- Reads/writes CRT controller cursor registers.
- Implements `cgascreenputc` for newline, tab, backspace, ordinary characters, scroll, and cursor update.
- Implements interrupt-safe `cgascreenputs` using `canlock` at high priority.
- Provides `cgapost(code)` to display a two-hex-digit POST code near the bottom of the screen.
- `screeninit()` initializes `cgapos` from hardware cursor registers and installs `screenputs`.

Important behavior:
- Screen memory is `KADDR(0xB8000)`.
- Scrolling moves the 24 lower lines up and clears the final line.
- Cursor position is tracked in byte offsets because each cell is character+attribute.

Dependencies:
- Depends on port I/O functions `inb`/`outb`, `KADDR`, and Plan 9 screenputs hook.

Notable risks:
- Assumes VGA-compatible text mode and 80x25 layout.
- Drops console output if called during interrupt and lock is already held.
