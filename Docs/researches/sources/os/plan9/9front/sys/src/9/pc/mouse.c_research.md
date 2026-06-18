# File Research: sources/os/plan9/9front/sys/src/9/pc/mouse.c

Implements PC mouse control and packet decoding for serial mice, PS/2 mice, IntelliMouse-style extensions, and Synaptics touchpads/trackpoints.

Key behavior:
- `ps2mouseputc()` decodes 3-byte PS/2 packets and optional 4-byte IntelliMouse packets. It sign-extends deltas, maps button bits, handles shift-right as middle-click through the `b[]` map, detects packet desynchronization by elapsed time, and sends motion through `mousetrack()`.
- `synmouseputc()` decodes 6-byte Synaptics absolute packets, distinguishes trackpoint packets from touchpad packets, performs simple palm/edge filtering, scales absolute touchpad coordinates to screen geometry from `gscreen`, suppresses accidental taps based on motion thresholds, and emits relative pointer motion.
- Control commands are parsed by `mousectl()` using `Cmdtab`: `accelerated`, `linear`, `res`, `ps2`, `ps2intellimouse`, `serial`, `reset`, `hwaccel`, `touchpad`, and `synaptic`.
- PS/2 setup and mode changes use `i8042auxenable()` and `i8042auxcmd()`.
- Serial setup uses `uartmouse()`/`uartsetmouseputc()` and the existing serial decoders declared in `screen.h`.

Important state includes `mousetype`, `intellimouse`, `packetsize`, `resolution`, acceleration flags, `synaptic`, `disabletouch`, and the configured serial `mouseport`.

Research notes:
- Depends on display state via `gscreen` for Synaptics coordinate scaling.
- Uses a `QLock` around control changes so command writes do not interleave controller reconfiguration.
- Touchpad logic is heuristic and device-specific, with dynamic edge calibration from observed min/max coordinates.
