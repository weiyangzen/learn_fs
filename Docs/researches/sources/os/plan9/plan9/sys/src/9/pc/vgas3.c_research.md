# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgas3.c

S3 VGA driver covering classic S3 page banking, linear framebuffer/MMIO setup, hardware cursor, ViRGE acceleration, blanking, and delegation to Savage acceleration. It defines PCI/device IDs for S3 ViRGE, Savage, VirtualPC, and related devices.

Device/page setup:
- `s3pageset()` programs CRTC bank registers `0x35` and `0x51`, with depth-dependent handling.
- `s3linear()` maps S3 PCI linear framebuffer, exports `s3screen`, and for supported Savage chips searches PCI BARs for a 512KB/16MB MMIO aperture and maps/export `savagemmio`.

Cursor:
- `s3enable()` sets cursor colors, computes cursor storage after visible framebuffer, writes base registers, loads arrow, and enables Microsoft Windows-format cursor.
- `s3load()` writes interleaved AND/XOR 64x64 cursor data using either linear storage or banked access depending on chip ID.
- `s3move()` handles offscreen-left/top by programming cursor offsets.
- `s3vsyncactive()` waits for a safe period to avoid hangs on some chips.

ViRGE acceleration:
- MMIO register offsets include source/destination base, stride, coordinates, command, FIFO/status.
- `waitforlinearfifo()`, `waitforfifo()`, and `waitforidle()` poll hardware status and count timeouts.
- `hwfill()` and `hwscroll()` use BitBLT-style commands.
- `s3drawinit()` installs acceleration for selected ViRGE IDs and calls external `savageinit()` for supported Savage IDs.

Blanking uses sequencer `CursorSyncCtl` sync bits but `hwblank` is not enabled due to comments about uncertain behavior. Exports `VGAdev vgas3dev` and `VGAcur vgas3cur`.
