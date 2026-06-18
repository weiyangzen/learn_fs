# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgamga4xx.c

Matrox G200/G400/G450/G550 VGA driver with framebuffer sizing, DAC cursor, DPMS blanking, and 2D acceleration.

Key responsibilities:
- Detects Matrox PCI IDs `MGA4xx`, `MGA550`, and `MGA200`.
- Maps a 16 KiB MMIO window and linear framebuffer.
- Probes actual video memory by writing/checking 2 MiB boundaries after enabling MGA mode.
- Implements DAC cursor controls through MMIO DAC registers at `0x3C00`.
- Implements DPMS blanking with sequencer and CRTC extension registers.
- Initializes 2D engine state and exports fill/scroll acceleration.

Important behavior:
- Cursor storage is placed at the last 4 KiB of the detected aperture.
- Cursor base address is programmed in 1 KiB units through indirect DAC cursor-address registers.
- Fill uses solid `DWGCTL` trap/rectangle operation; scroll uses bitblt with overlap direction handling.
- `mga4xxdrawinit` sets pitch, memory access format for 8/16/24/32 bpp, fill, scroll, and blank callbacks.

Exports:
- `VGAdev vgamga4xxdev` named `mga4xx`.
- `VGAcur vgamga4xxcur` named `mga4xxhwgc`.

Notable risks:
- Memory-size probe is described as “sketchy” and writes into framebuffer memory.
- FIFO wait has a very small fixed timeout and only prints on timeout.
- Acceleration assumes supported depth and silently returns without acceleration for others.
