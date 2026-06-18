# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/tr2post.h

Shared declarations and data structures for `tr2post`. It defines limits, charlib path, global renderer/font state, glyph/font mapping structs, and prototypes for parsing, drawing, picture inclusion, page/font/string output, and utility functions.

Integration points:
- Included across `tr2post` implementation files.
- Defines `struct charent`, `struct psfent`, `struct troffont`, and `struct pfnament`, which are central to mapping troff glyphs to PostScript fonts.

Risks:
- Large global surface area makes hidden coupling easy.
- Fixed constants such as `MAXSPECHARS`, `MAXTOKENSIZE`, and `CHARLIB` constrain inputs and install layout.
