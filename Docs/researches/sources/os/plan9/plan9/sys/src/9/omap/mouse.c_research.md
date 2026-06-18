# File Research: sources/os/plan9/plan9/sys/src/9/omap/mouse.c

Mouse packet decoding and control handling, mainly for PS/2-format mouse streams.

Key responsibilities:
- Decodes 3-byte PS/2 mouse packets and 4-byte Intellimouse/AccuPoint packets.
- Maps button bits, including shift-right to middle-button behavior through `mouseshifted`.
- Handles packet resynchronization after long idle gaps.
- Sends movement/button events to `mousetrack`.
- Provides `mousectl()` command handling for acceleration, resolution, linear mode, Intellimouse mode, reset, and hardware acceleration flags.

Important behavior:
- `ps2mouseputc` signs-extends X/Y deltas from packet status bits and negates Y.
- Intellimouse packets can switch back to 3-byte packet mode if the fourth byte looks like a new first byte.
- Serial mouse command reports unsupported.

Dependencies:
- Uses devmouse functions from `screen.h`, Plan 9 command parsing, `MACHP(0)->ticks`, and the global keyboard shift state.

Notable risks:
- The actual PS/2 enable path is commented out, so this file provides decoding/control logic but not a complete OMAP hardware path.
- Several control settings record state but do not program hardware because the low-level controller hooks are absent/commented.
