# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/edid.c

Parses 128-byte VESA EDID blocks into `Edid` and `Modelist` data. It validates the EDID header and checksum, decodes manufacturer/product/serial/date/display features, and records DPMS/digital/monochrome/GTF flags.

It builds modes from detailed timing blocks first, then standard timings, descriptor-supplied extra timings, and established VESA timings. `edidshift` repairs buffers where the EDID header appears wrapped rather than at byte zero, useful for some Intel access paths.

`printedid` emits monitor identity, range limits, flags, and decoded modes. The mode output is consumed by `main.c` as a fallback when the monitor database lacks the requested mode.
