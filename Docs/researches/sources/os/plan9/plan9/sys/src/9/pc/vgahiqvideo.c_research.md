# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgahiqvideo.c

Chips & Technologies HiQVideo/HiQV32 linear framebuffer and hardware cursor support.

Key responsibilities:
- Detects PCI vendor `0x102C` devices `0x00C0`, `0x00E0`, `0x00E4`, and `0x00E5`.
- Determines video-memory size from device type or extension register `0x43`.
- Enables linear PCI framebuffer and registers `hiqvideoscreen`.
- Uses the last 4 KiB of framebuffer as cursor storage, stored in `scr->mmio`.
- Implements 32x32 hardware cursor through extension registers at `0x3D6/0x3D7`.

Important behavior:
- Cursor enable and storage address are programmed through XR registers `0xA0`, `0xA2`, and `0xA3`.
- Cursor color programming temporarily toggles XR `0x80`.
- Negative cursor coordinates are encoded with high-bit flags in position registers.
- `hiqvideolinear` is a no-op because enable already maps the linear framebuffer.

Exports:
- `VGAdev vgahiqvideodev` named `hiqvideo`.
- `VGAcur vgahiqvideocur` named `hiqvideohwgc`.

Notable risks:
- Uses `scr->mmio` as a pointer into framebuffer cursor storage, not MMIO registers, which differs from most VGA drivers.
- Only selected HiQVideo IDs are supported.
