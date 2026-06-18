# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/p9bitpost/pslib.c

`pslib.c` provides PostScript image output support for `p9bitpost`. It initializes library state, writes a DSC preamble and image prologue, embeds an indexed Plan 9 color map or grayscale/RGB setup, writes optional patch PostScript, and emits trailer/page markers.

`image2psfile()` converts unsupported high-depth image channels to 24-bit RGB, computes image placement and scaling from paper size, margins, dpi, magnification, and landscape mode, then writes `doimage` invocation and ASCII85-encoded image data. `imagebits()` compacts image rows, inverts bytes, handles sub-byte alignment, encodes in ASCII85, and terminates the stream.

Large commented sections show older Inferno/Tk text-printing support that is no longer compiled.
