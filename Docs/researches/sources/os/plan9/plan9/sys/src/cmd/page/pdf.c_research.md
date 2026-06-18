# File Research: sources/os/plan9/plan9/sys/src/cmd/page/pdf.c

Implements PDF support for `page` through Ghostscript. It includes `pdfprolog.c` as a C string, opens or spools the PDF, starts Ghostscript with delayed safer mode, loads the prolog, opens the PDF in Ghostscript, and asks for page count.

`PDFInfo` embeds `GSInfo` and stores per-page crop boxes. `pdfbbox` queries `/CropBox`, parses a four-number rectangle, and falls back to a trailer-level bounding box if a page has no usable crop box.

`pdfdrawpage` sends `DoPDFPage` for the page number, reads the generated Plan 9 image from the Ghostscript data fd, and waits for Ghostscript completion. Page names are simple `p N` labels.
