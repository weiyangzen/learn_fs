# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vga.h

Defines the shared `aux/vga` controller model, register constants, data structures, flags, and extern declarations.

Key responsibilities:
- Defines standard VGA I/O ports, palette constants, reference clock constants, and name length.
- Defines `Ctlr` with phase callbacks `snarf`, `options`, `init`, `load`, `dump`.
- Defines controller phase/capability/use flags such as `Fsnarf`, `Hlinear`, `Ulinear`, `Hpclk2x8`, `Uclk2`.
- Defines `Attr`, `Mode`, `Modelist`, `Edid`, `Flag`, and the central `Vga` state structure.
- Documents how `mode->x/y` differ from `vga->virtx/virty`, including panning and stride alignment implications.
- Declares all controller instances and support functions across the `aux/vga` program.

Important interfaces:
- All files in this group include this header.
- Declares VESA entry points, VGA register helpers, PCI helpers, EDID helpers, RAMDAC helpers, S3 helpers, and many controller symbols.

Notes:
- The header is the primary integration contract for this controller framework.
- It includes a global `Biobuf stdout` declaration in the main section.
