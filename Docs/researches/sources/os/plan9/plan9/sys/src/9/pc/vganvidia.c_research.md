# File Research: sources/os/plan9/plan9/sys/src/9/pc/vganvidia.c

NVIDIA VGA driver using MMIO, hardware cursor, DMA push buffer setup, 2D acceleration, and blanking. File includes an NVIDIA 2003 copyright/license notice and `nv_dma.h`.

Device setup:
- `nvidiapci()` matches vendor `0x10DE` display devices with device ID at least `0x20`.
- `nvidiaenable()` maps BAR0 MMIO, maps linear framebuffer, exports `nvidiammio` and `nvidiascreen`, and computes video memory size using PFB registers or chipset-specific host bridge config for some generations.

Cursor:
- Cursor position register is at PRAMDAC offset `0x0300`.
- `nvidiacurload()` handles early NV chips differently from later chips: early chips use PRAMIN cursor memory, later chips place cursor data near the end of framebuffer and programs CRTC cursor-location registers.
- Cursor pixels are expanded into 32-bit values, offset is saved, and CRTC register `0x31` enables cursor.
- `nvidiacurmove()` writes packed X/Y to MMIO cursor position.

Acceleration:
- Global `nv` tracks DMA push buffer base/current/put/free/max.
- `nvresetgraphics()` allocates/maps a 128KB DMA buffer near video memory end, initializes object handles and surface/pattern/rect/line formats by depth, sets ROP, and waits idle.
- `nvidiahwfill()` emits solid rectangle commands.
- `nvidiahwscroll()` emits blit commands.
- `nvdmawait()`, `nvdmastart()`, `nvdmakickoff()`, `writeput()`, and `readget()` manage the FIFO/DMA ring.

Blanking uses sequencer register 1 and CRTC register `0x1A`. `nvidiadrawinit()` installs blank, fill, and scroll callbacks and sets `hwblank`.

Exports `VGAdev vganvidiadev` and `VGAcur vganvidiacur`.
