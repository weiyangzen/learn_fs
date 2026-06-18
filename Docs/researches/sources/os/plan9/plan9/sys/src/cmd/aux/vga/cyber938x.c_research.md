# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/cyber938x.c

Controller backend for Trident Cyber938x and related Cyber/ProVidia/CyberBlade chips.

Core behavior:
- Handles old/new sequencer register modes.
- Accesses DAC Pixel Command Register via four Pixmask reads.
- Saves sequencer, CRTC, graphics, old registers, and PCR.
- Determines memory size from CRTC register `0x1F`.
- Determines LCD panel size from graphics register `0x52`.
- Supports linear framebuffer.
- Programs depth-specific PCR and pixel-bus register values for 8/16/24 bpp.
- Applies revision-specific register tweaks for ProVidia 9685, Cyber9320/9382/9385/9388, Cyber9525/DVD, and CyberBlade variants.

Ctlrs:
- `cyber938x`
- `cyber938xhwgc` placeholder.

Notable risks:
- Comments state ProVidia 9685 support is incomplete, with no clock code and only 640x480x8 working.
- Revision-specific magic values are hardware-fragile.
