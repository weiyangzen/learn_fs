# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgamach64xx.c

ATI Mach64/Rage family VGA driver with PCI enable, linear/MMIO mapping, hardware cursor, optional panning, 2D acceleration, LCD blanking, and overlay control/write path. It supports multiple CT/ET/GT/VT/LT/Rage IDs through the `mach64s[]` table, recording chip class, overlay clock, and PRO capability.

Device setup:
- `mach64xxenable()` matches ATI PCI vendor `0x1002`, records chip ID, and derives I/O base, defaulting to `0x2EC` for CT-like devices.
- `mach64xxlinear()` maps framebuffer with `vgalinearpci()`, marks the embedded MMIO register page uncached via `mtrr()`, sets `scr->mmio` to the final 1KB of aperture, and exports MMIO/screen segments.
- `ior32()`/`iow32()` abstract register access via I/O ports or MMIO using the `mmoffset[]` register map.

Cursor behavior:
- Uses Mach64 hardware cursor registers `CurClr0`, `CurClr1`, `CurOffset`, `CurHVposn`, `CurHVoff`, and `GenTestCntl`.
- `mach64xxcurload()` writes a 64x64 cursor pattern into framebuffer storage and enables bit `0x80`.
- `mach64xxcurmove()` optionally pans `physgscreenr` when `panning` is active, adjusts offsets for negative coordinates, and updates cursor position.
- `VGAcur` sets `doespanning = 1`.

Acceleration:
- `initengine()` resets and initializes the GUI engine, sets pitch, clipping, mix, source/destination, pixel width, and derives reference clock/revision from BIOS/config registers.
- `mach64hwfill()` and `mach64hwscroll()` implement accelerated rectangle fill and screen-to-screen copy, including special 24bpp coordinate/pitch handling.
- `mach64xxdrawinit()` installs acceleration when usable and sets LCD-specific blanking for LT/Rage Mobility IDs.

Overlay:
- Overlay state is global (`ovl_chan`, width/height/format/frame bytes, `mach64overlay`).
- `mach64xxovlctl()` parses commands: `openctl`, `closectl`, `configure`, `enable`, and `status`.
- Only `"YUYV"` configuration is accepted; scaler/overlay registers are programmed differently for revision B.
- `mach64xxovlwrite()` copies user data into overlay framebuffer storage circularly by frame size.

Notable risks:
- Overlay control uses global state, so it is effectively single-controller/single-owner.
- `mach64blank()` is present but disabled because comments say it disrupts screen timings; LCD blanking is used selectively.
- The overlay code uses many empirically derived register choices and old GLX-derived clock logic.
