# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmacpictop.h

Provides macro helpers for writing Classic MacOS QuickDraw PICT structures and opcodes. It is included by `gdevmac.h` and used heavily by `gdevmac.c` and `gdevmacxf.c`.

The first macro layer writes primitive byte/int/long values, QuickDraw `Point`, `Rect`, `Region`, `Pattern`, RGB colors, color tables, pixmaps, PackBits image data, and Pascal strings.

The opcode layer covers many PICT operations: clipping, patterns, text font/face/mode/size, colors, lines, text, rectangles, rounded rectangles, ovals, arcs, bitmap/pixmap image transfer, and end-picture handling.

`PICTWriteDataPackBits` either copies raw data for small rasters or calls QuickDraw `PackBits` per row and writes row lengths with correct byte padding. It allocates a temporary compression buffer.

The Ghostscript helper macros `GSSetStdCol`, `GSSetFgCol`, and `GSSetBkCol` convert Ghostscript color indices through the device’s `map_color_rgb` procedure and emit PICT RGB color opcodes.

This header is macro-heavy and assumes pointer expressions are mutable lvalues; it is tightly coupled to Classic MacOS data layout and QuickDraw APIs.
