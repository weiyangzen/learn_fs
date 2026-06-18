# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/p9bitpost/p9bitpost.c

Plan 9 bitmap-to-PostScript command-line frontend.

Key responsibilities:
- Parses DPI, debug, magnification, landscape, patch string, and paper-size options.
- Reads a Plan 9 image into a `Memimage`.
- Initializes `pslib`, applies options, and writes PostScript image output.

Important behavior:
- Defaults to stdin and file label `<stdin>`.
- `-m` can set x and y magnification separately.
- `-P` passes a raw PostScript patch string through to `pslib`.

Dependencies:
- Uses Plan 9 `draw`, `memdraw`, and `pslib`.

Notable risks:
- Option parsing manually indexes `argv[++i]` for some options and can fall into usage on missing values.
