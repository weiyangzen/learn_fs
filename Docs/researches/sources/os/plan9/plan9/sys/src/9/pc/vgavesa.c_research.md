# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgavesa.c

## Purpose
Generic VGA driver that relies on the VESA BIOS Extension to discover the current linear framebuffer and optionally uses a software backing screen flushed to the real framebuffer.

## Main Interfaces
- Exports `VGAdev vgavesadev` named `vesa`.
- Supplies `linear` callback `vesalinear`.
- Supplies `flush` callback `vesaflush`.

## Implementation Notes
- VBE calls use `/dev/realmodemem` and `/dev/realmode` to place a request buffer at `RMBUF` and invoke BIOS interrupt `0x10`.
- `vbecheck` requires VESA signature and VBE version 2 or newer.
- `vesalinear` asks for current mode, checks graphics and linear-framebuffer attributes, reads physical framebuffer address from mode info, and estimates usable framebuffer size.
- PCI BAR matching is used to grow the mapping to the real BAR size when possible; fallback heuristics round to at least 4 MiB and cap at 16 MiB.
- With `Usesoftscreen`, the hard framebuffer is hidden from the generic screen code and `vesaflush` copies dirty rectangles from software screen data.

## Dependencies And Risks
- Requires functioning real-mode BIOS call devices.
- The code comments note Bochs loses top bits of the mode number, so the linear-mode bit in current mode is not trusted.
- Software flush assumes word-aligned memmove spans based on `Memimage` layout.
