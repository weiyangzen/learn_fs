# File Research: sources/os/plan9/plan9/sys/src/cmd/page/ps.c

Implements PostScript support for `page`. It scans DSC comments to identify page offsets, page labels, trailer position, document bounding box, page order, orientation, and whether translation tricks are safe.

`PSInfo` stores Ghostscript state, default bounding box, page offset table, whether the document is “clueless”/forward-only, the `%!` offset, and related metadata. If no page boundaries are found, the file is treated as one stream rendered forward-only.

`rdbbox` parses and normalizes bounding boxes, expanding likely page-sized documents to A4 or 8.5x11 unless true bounding-box mode is requested. `repaginate` can collapse multiple physical pages into one logical page group.

Rendering writes either just the requested page slice or header/page/trailer slices to Ghostscript, depending on `goodps`. A newline is sent after page data to avoid a Ghostscript read-ahead deadlock on carriage-return-terminated input.
