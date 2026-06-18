# File Research: sources/os/plan9/9front/sys/src/cmd/page.c

## Role

Implements Plan 9’s graphical document/image viewer. It can open images, directories, archives, compressed files, PostScript/PDF/troff/text/html/dvi/doc inputs through filters, and EPUB-like directory trees.

## Page Model

`Page` forms a recursive tree with parent, child, sibling, tail, and LRU links. A page can have an opener function, backing fd/path/filter data, loaded `Image`, extension command, and delimiter used in page addresses.

The viewer tracks current page, read-ahead direction, image memory limit, view generation, zoom/resize/rotate settings, and an affine warp matrix for pan/zoom display.

## Input And Decoding

`popenfile` detects directories, EPUB container metadata, and file types using Plan 9 `file -m`. It dispatches formats to:

- `popenimg` for image converters.
- `popengs`/`popenpdf` for Ghostscript and PDF page extraction.
- `popentape` for archive mounting through zip/tar filesystems.
- `popenfilter` for decompression filters.
- `popenepub` for EPUB spine expansion.

Non-seekable or changing streams are spooled to temporary files.

## Rendering And Caching

`openpage` applies rotate/resize filters before `readimage`. `loadpages` reads ahead from the current page while respecting an LRU image memory limit. `unloadpages` frees images from the LRU tail.

Drawing uses affine warp operations to render the current image, draws a frame, and fills background differences. Pan/zoom mutate `warpmat`; fit-width/fit-height reload through image resize filters.

## UI

Mouse buttons support drag panning, command menu, page menu, and scrolling. Keyboard commands support original size, zoom, fit, rotate, next/previous, snarf page address, write bitmap, open external decoder, clone view, and quit.

The program also listens on the `image` plumb port to show files or inline data and supports page-address jumps.
