# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postgif/postgif.c

GIF87a-to-PostScript translator.

Key responsibilities:
- Emits PostScript job structure and copies the `POSTGIF` prologue.
- Reads GIF87a screen descriptors, global/local color maps, image descriptors, extension blocks, and LZW image data.
- Converts GIF pixels to either indexed color-table data or grayscale hex image data.
- Supports negative/inverted colors, grayscale output, gamma adjustment, alignment, forms per page, page selection, magnification, orientation, offsets, copied PostScript, and prologue override.
- Emits screen/page wrappers through `gifscreen` and image data through `gifimage`.

Input/control flow:
- `readgif()` initializes GIF code-size lookup table, verifies the GIF87a signature, reads the logical screen descriptor, loads or synthesizes a global color map, starts a page, and processes image/extension/terminator blocks.
- `readimage()` reads image metadata, chooses local or global color maps, allocates `pmap`, decodes LZW codes into pixel indices, skips remaining raster sub-blocks, writes the image, and restores the global map after local-map images.
- `initstbl()`, `getcode()`, `putcode()`, and `firstof()` implement GIF LZW table state.
- `writeimage()` emits color tables and pixel streams, handling interlace pass reordering when needed.
- `readextensionblock()` skips extension sub-block chains.
- `writebgscr()` and `writeendscr()` wrap each GIF screen as one PostScript page.

Important behavior:
- If the first six bytes are not `GIF87a`, it skips 122 bytes and tries again, suggesting support for a wrapper/header format.
- Grayscale uses weighted RGB conversion with defaults `0.3`, `0.59`, `0.11`.
- Gamma correction is applied to color maps when `-G` is used.
- Bounding box is tracked with `bburx` and `bbury`.

Dependencies:
- Shared common layer: `comments.h`, `gen.h`, `path.h`, `ext.h`, `cat()`, `out_list()`, `in_olist()`, `error()`, `interrupt()`.
- Links with math support for `pow()` depending on build context.
- Expects `POSTGIF` prologue procedures `setup`, `gifscreen`, `gifimage`, and `done`.

Risks and quirks:
- Accepts only `GIF87a`; GIF89a is rejected.
- Most `fread()` calls do not check return counts.
- LZW decode writes to `pmap` without checking `pmindex < imagewidth * imageheight`.
- Global `terminate` is not reset inside `readgif()`, which can affect multiple input files in one run.
- Graphic control extensions are skipped, so transparency/delay/disposal metadata is ignored.
- Interlace lookup arrays allocated in `writeimage()` are not freed.
