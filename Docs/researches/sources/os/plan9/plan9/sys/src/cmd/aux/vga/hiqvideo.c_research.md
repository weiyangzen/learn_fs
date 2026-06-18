# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/hiqvideo.c

Controller backend for Chips & Technologies HiQVideo/HiQV32 chips, including 69000 and 65550/65554/65555.

Core behavior:
- Locates PCI vendor `0x102C` and supported device IDs.
- Saves flat-panel extension registers, multimedia registers, extended CRTC registers, and configuration extension registers.
- Determines max dot clock from chip and voltage state.
- Determines framebuffer memory size from chip-specific registers.
- Advertises linear framebuffer.
- Computes programmable DCLK PLL within documented constraints.
- Avoids programming DCLK when output is LCD according to flat-panel register state.
- Supports 8/16/32 bpp.
- Programs extended CRTC overflow, pixel format, linear aperture, and DCLK registers.

Ctlrs:
- `hiqvideo`
- `hiqvideohwgc` placeholder.

Notable risks:
- Header comment says depths other than 8 are too slow.
- 69000 extensions over 65550 are not fully considered.
- PLL code uses floating-point search and assumes stable register constraints.
