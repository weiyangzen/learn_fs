# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/imgexam.c

Examines embedded Word image containers and image headers. It identifies image type, validates basic dimensions/format constraints, and fills `imagedata_type`.

Supported recognition:

- DIB/BMP headers with uncompressed, RLE4, and RLE8 variants.
- Baseline/extended sequential JPEG usable for PostScript Level 2.
- PNG with non-interlaced zlib compression, no unsupported alpha/component forms.
- WMF stub examination exists but currently returns false.
- Word 6/7 image records.
- Word 8/9/10 OfficeArt records.

Important functions:

- `bExamineDIB()` parses DIB headers, validates planes, size, bit depth, compression, palette, component count.
- `bExamineJPEG()` walks JPEG markers, rejects unsupported SOF types, records Adobe APP14, dimensions, component count, and compression.
- `bExaminePNG()` validates PNG signature/chunks, extracts IHDR/PLTE, rejects unsupported interlace/filter/compression/alpha/component combinations, and creates default grayscale palette when needed.
- `tFind6Image()` locates Word 6/7 embedded DIB records.
- `tFind8Image()` scans OfficeArt records and identifies EMF, WMF, PICT, JPEG, PNG, and DIB payload starts.
- `vImage2Papersize()` scales oversized images to fit configured page size for non-RISC OS builds.
- `eExamineImage()` is the public entry point: reads the Word image wrapper, computes scaled physical size, dispatches image-specific examination, and returns no/minimal/full information.

The module is defensive: many malformed or unsupported cases degrade to minimal image information rather than attempting full translation.
