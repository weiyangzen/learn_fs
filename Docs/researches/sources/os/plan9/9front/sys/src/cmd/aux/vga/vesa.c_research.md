# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vesa.c

Implements VESA BIOS Extension support for `aux/vga`.

Key responsibilities:
- Wraps real-mode VBE BIOS calls through `/dev/realmode` and `/dev/realmodemem`.
- Maintains a 1 MB memory shadow with page-valid/dirty tracking for real-mode buffers.
- Detects VBE 2.0+ support, enumerates VBE modes, queries mode information, and switches modes.
- Converts VBE framebuffer mode info into Plan 9 `Mode` records with size, channel, depth, stride, and VBE mode ID attributes.
- Supports explicit VBE mode IDs, mode scans, and fallback scanning of unoffered `0x100..0x1ff` modes.
- Reads DDC EDID using VBE function `0x4F15`.
- Handles Intel display selection/scaling extensions and has disabled NVIDIA scaling support due to a noted modeset breakage.
- Provides text-mode restore through `vesatextmode`.

Important interfaces:
- Exports `Ctlr vesa`, `Ctlr softhwgc`, `dbvesa`, `dbvesamode`, and `vesatextmode`.
- Uses `Vbe` private structure and `Vmode` intermediate mode representation.
- Integrates with `Vga` by installing `vga->vesa`, `vga->ctlr`, and a soft hardware cursor controller.

Notes:
- `load` resets scaling, optionally switches display output, sets VBE graphics mode with linear framebuffer/no-clear bits, then applies requested scaling.
- `rgbmask2chan` derives Plan 9 channel strings from VBE direct-color masks.
- `fixbios` patches a known Intel Cantiga mode alias table bug for 1440x900x32.
