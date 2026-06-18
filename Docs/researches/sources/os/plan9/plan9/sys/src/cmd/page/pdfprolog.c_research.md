# File Research: sources/os/plan9/plan9/sys/src/cmd/page/pdfprolog.c

A small C string fragment of Ghostscript/PDF PostScript prolog consumed by `pdf.c`.

It initializes PDF-related variables, defines `DoPDFPage` as page lookup plus rendering, and overrides page setup to honor `CropBox`, `Rotate`, page size, and page offset via `setpagedevice`.

The file is not standalone C logic; it is included directly into a string literal assignment.
