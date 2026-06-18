# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlxm.c

Implements `lxm5700m`, a monochrome Lexmark 5700 inkjet printer device. It is designed around the printer’s dual black printhead columns and supports a tunable `HeadSeparation` parameter.

The device subclass `lxm_device` extends `gx_device_printer` with `headSeparation`. Parameters are exposed through `lxm_get_params` and `lxm_put_params`, with accepted separation range 1 to 32 and default 16.

`lxm5700m_print_page` emits initialization commands, scans for non-blank swipes, copies 208-line swipe bands, computes horizontal extents, and builds compressed column data. Output alternates `RIGHTWARD`/`LEFTWARD` direction to account for which physical printhead handles even/odd columns.

Compression uses a per-column directory of 13 16-bit sectors for a 208-pixel column. Only non-empty sector bitmaps are emitted after the directory. Swipe overlap is fixed at 104 lines.

The code dynamically grows the swipe output buffer when needed. It is tightly bound to reverse-engineered Lexmark protocol details and includes comments noting uncertainty about mechanical behavior.
