# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/vesa.c

This file implements VESA BIOS/VBE services through a small guest ROM and port-mediated helper thread.

Key behavior:
- Installs a synthetic option ROM at 0xc0000, BIOS vector pointer, OEM strings, and a mode table.
- Uses ports 0xfee0-0xfeef as a protocol between real-mode guest BIOS code and the `vesathread`.
- Handles VBE functions for controller info, mode info, set/get mode, logical scanline length, DAC palette format, palette data, and DDC/EDID.
- Synthesizes VBE mode descriptors and EDID timing blocks from configured `VgaMode` entries.
- Manages palette updates through `vgasetpal`/`vgagetpal`.
- `vesainit` appends standard legacy VESA modes and starts the helper thread.

Integration and risks:
- Depends on `vga.c` globals for modes, framebuffer address/size, and display state.
- Real-mode BIOS interface is custom and partial; unsupported VBE functions return failure and log debug messages.
