# File Research: sources/os/plan9/plan9/sys/src/9/pc/mouse.c

PC mouse control and packet decoding for PS/2 and serial mice.

Key elements:
- Supports mouse types `Mouseother`, `Mouseserial`, and `MousePS2`.
- `ps2mouseputc` decodes PS/2 3-byte packets and IntelliMouse/AccuPoint 4-byte packets, including stream resynchronization after long gaps.
- Shift plus right-button is mapped as middle-button behavior.
- Extra IntelliMouse/AccuPoint bytes are mapped to buttons 4/5 using simple wheel/sign logic.
- `ps2mouse`, `resetmouse`, `setres`, `setintellimouse`, `setaccelerated`, `setlinear` configure hardware through i8042 aux commands or serial mouse handlers.
- `mousectl` parses architecture control commands: `ps2`, `ps2intellimouse`, `serial`, `res`, `reset`, `accelerated`, `linear`, `hwaccel`, `intellimouse`.

Interactions:
- Feeds decoded events to `mousetrack`.
- Uses `i8042auxenable`, `i8042auxcmd`, `i8250mouse`, `i8250setmouseputc`.
- Shares screen/draw cursor definitions via `screen.h`.

Research notes:
- Input support only; no filesystem behavior.
- The code adapts packet size dynamically for mixed laptop TrackPoint/external-mouse scenarios.
