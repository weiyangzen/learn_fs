# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postgif/postgif.c

`postgif.c` converts GIF87a images into PostScript using the `postgif.ps` prologue.

Main flow:
- `main()` initializes signals, writes header/prologue, parses options, sets up, reads input GIFs, and emits trailer.
- `readgif()` validates the GIF87a signature, reads logical screen descriptor/global color map, starts a PostScript page, processes image/extension/terminator blocks, and closes the page.
- `readimage()` reads an image descriptor, optional local color map, LZW minimum code size, decompresses image codes, drains remaining data sub-blocks, and calls `writeimage()`.
- `writeimage()` emits PostScript setup, color/grayscale lookup tables, and hex image data, handling interlaced and non-interlaced order.
- `readextensionblock()` skips GIF extension blocks.

GIF decoding:
- LZW tables are `prefix[4096]`, `suffix[4096]`, and `cstbl[4096]`.
- `initstbl()`, `nextbyte()`, `getcode()`, `putcode()`, and `firstof()` implement decompression.
- `pmap` stores decompressed pixel indices for the whole image.
- Interlace reconstruction uses pass order 0,4,2,1 rows.

Color handling:
- Global/local RGB color maps are read or a default grayscale map is generated.
- `-g` switches grayscale output.
- `-f` negates colors.
- `-G` applies gamma correction.
- Luminance weights default to 0.3, 0.59, 0.11.

Options:
- Includes aspect, copies, negative, grayscale, alignment, magnification, forms per page, page list, orientation, offsets, copy-through, encoding placeholder, debug, gamma, ignore-fatal, prologue, pass-through.

Limitations and risks:
- Only accepts GIF87a; GIF89a is not supported.
- Contains a fallback that skips 122 bytes and retries signature matching, likely for wrapped input formats.
- Uses whole-image decompression into memory.
- `nextbyte()` treats zero sub-block before end code as fatal.
- No accounting support unlike several sibling tools.
- Old-style globals and sparse error checking around `fread()` make malformed/truncated files risky.

Filesystem relevance: none direct; this is image conversion code.
