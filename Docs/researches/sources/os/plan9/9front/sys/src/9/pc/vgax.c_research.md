# File Research: sources/os/plan9/9front/sys/src/9/pc/vgax.c

Shared VGA indexed register access helpers for the PC VGA subsystem.

Key behavior:
- `vgaxi` reads indexed VGA registers for sequencer, CRTC, graphics, and attribute controller ports.
- `vgaxo` writes indexed VGA registers for those same port families.
- Access is serialized with a static interrupt lock because VGA index/data ports are shared mutable state.
- Attribute-controller access handles the VGA flip-flop by reading `Status1` before writes and restores palette access bit `0x20` after palette-index operations.

Notable dependencies:
- Low-level `inb`/`outb` port I/O.
- VGA port constants from `screen.h` / `io.h`.

Research notes:
- The code avoids combined outport writes because some S3 chips have trouble with that for some registers.
- Unknown index port families return `-1`.
