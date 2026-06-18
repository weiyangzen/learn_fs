# File Research: sources/os/plan9/9front/sys/src/9/pc/cga.c

Text-mode CGA console output backend for early/legacy PC display.

Key responsibilities:
- Maintains an 80x25 text console at physical `0xB8000`.
- Converts Unicode runes to Code Page 437 character cells.
- Implements newline, tab, backspace, scroll, cursor movement, and screen attribute updates.
- Transfers existing CGA screen contents into `kmesg` during first initialization.
- Installs `screenputs` unless disabled by `*nocga`.

Important behavior:
- Uses a lock and avoids deadlock by dropping interrupt-time prints if the console lock is unavailable.
- Maintains partial UTF-8 rune bytes across calls.
- Scrolls by moving screen memory up one row and clearing the final row.

Dependencies:
- Depends on VGA/CGA CRT controller I/O ports, `KADDR`, `kmesg`, UTF/rune helpers, and boot configuration.

Notable risks:
- Code Page 437 lookup is linear for every output rune.
- Direct writes to physical text memory assume a valid CGA-compatible text buffer.
