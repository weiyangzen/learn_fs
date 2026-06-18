# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/kbds.c

## Role

`kbds.c` converts incoming VNC/X11 keysyms into Plan 9 keyboard events for the VNC server's private `/dev/kbdin`.

## Main Behavior

- Provides a `vnckeys[]` table for VNC special keysyms in the `0xff00` range.
- Maps common special keys to Plan 9 runes such as arrows, home/end, page up/down, shift/control/alt, delete, escape, and keypad symbols.
- Uses `ksym2utf.h` to map X11 keysyms to Unicode runes.
- `vncputc()` writes null-terminated `r%C` key-down or `R%C` key-up records to `kbdin`.

## Notable Limitations And Risk Areas

- Unknown special keysyms are ignored.
- Mapping coverage is limited to the included tables and explicit special-key table.
- Writes are skipped when `kbdin` is negative.
