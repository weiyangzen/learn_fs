# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/ext.h

External global and helper declarations for portable PostScript translator code.

Key responsibilities:
- Declares process globals `argc`, `argv`, exit/debug/ignore flags, line/byte position, program name, temp file, and font encoding.
- Declares bounding-box and encoding globals.
- Declares getopt globals.
- Prototypes common helpers such as `cat`, `error`, `out_list`, `setencoding`, `interrupt`, and `tempnam`.

Notable behavior:
- Designed for older C code shared across multiple PostScript tools.
