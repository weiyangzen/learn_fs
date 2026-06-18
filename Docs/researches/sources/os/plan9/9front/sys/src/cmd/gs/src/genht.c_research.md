# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/genht.c

Build-time generator for compiling PostScript halftone resources into C data.

Key behavior:
- Reads a constrained PostScript halftone resource file into memory.
- Parses HalftoneType 5 prefixes and HalftoneType 3 halftone entries with Width, Height, and ASCIIHex Thresholds.
- Converts threshold bytes into Ghostscript halftone order data through `ht_order_procs_short.construct_order`.
- Emits C arrays for levels and bit data plus `gx_device_halftone_resource_t` structures.
- Writes a `gs_dht_<prefix>` procedure returning the static halftone-resource table.

Notable dependencies:
- Uses Ghostscript halftone and stream code: `gxdhtres.h`, `gxhttile.h`, `gxtmap.h`, `strimpl.h`, `sstring.h`.
- Includes implementation files directly (`gxhtbit.c`, `scantab.c`, `sstring.c`) to avoid a separate link step.

Research notes:
- The parser is intentionally narrow and ignores most PostScript that does not match the expected resource shape.
- It includes GC and stream stubs required by the included implementation code.
