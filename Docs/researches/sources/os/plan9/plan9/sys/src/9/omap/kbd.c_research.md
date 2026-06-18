# File Research: sources/os/plan9/plan9/sys/src/9/omap/kbd.c

OMAP keyboard scan-code translation for systems without a native keyboard controller, adapted from the PC PS/2 keyboard path.

Key responsibilities:
- Defines scan-code translation tables for normal, shifted, escaped, AltGr, control, control-escaped, and shifted-escaped states.
- Maintains independent internal and external `Kbscan` state machines.
- Converts scan codes to Plan 9 keyboard queue runes via `kbdputc(kbdq, ...)`.
- Tracks modifier state: shift, control, Alt/Latin compose, AltGr, caps lock, num lock, and mouse-button pseudo-keys.
- Supports Latin-1 compose collection through `latin1()`.
- Provides `kbdputmap()` and `kbdgetmap()` for runtime keyboard map mutation/query.
- Enables minimal keyboard state in `kbdenable()`.

Important behavior:
- `Ctl-Alt-Del` exits through `exit(0)`.
- `Latin` starts compose collection unless control is held, avoiding common VM focus-release behavior from `Ctl-Alt`.
- Shift updates the global `mouseshifted`, affecting mouse button mapping in `mouse.c`.
- F11 turns keyboard debug prints on; F12 turns them off.
- Mouse pseudo-key events can call `kbdmouse`.

Dependencies:
- Uses Plan 9 queue/global keyboard state from the port layer.
- Depends on `latin1`, `kbdputc`, `kbdq`, `error`, and Plan 9 error strings.

Notable risks:
- This is a scan-code table implementation, so behavior depends heavily on correct table entries.
- Some map arrays include mostly empty entries and special private-use rune encodings.
- The bounds check uses `sizeof kbtab`, which is byte size rather than `Nscan`; it is harmless here because entries are `Rune` and `c` is already masked to 7 bits, but it is semantically loose.
