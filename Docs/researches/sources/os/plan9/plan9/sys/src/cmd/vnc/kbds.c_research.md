# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/kbds.c

VNC server-side keyboard input translator from RFB/X keysyms into Plan 9 console runes.

Key responsibilities:
- Maps VNC/X special keysyms to Plan 9 keyboard constants.
- Uses `ksym2utf.h` to map X keysyms to Unicode runes.
- Tracks modifier state: Alt/Latin, caps, control, num, and shift.
- Implements Plan 9 Latin compose collection through `latin1()`.
- Sends resulting characters to the console queue via `kbdputc()`.

Important behavior:
- Key-up events only affect modifier state.
- Control modifies normal characters with `c &= 0x1f`.
- Latin starts compose collection and buffers up to five runes.
- Unknown special keys are ignored.

Risks:
- `shift` and `num` state is tracked but mostly unused in this translator.
- Mapping coverage depends on the generated `ksym2utf` table.
