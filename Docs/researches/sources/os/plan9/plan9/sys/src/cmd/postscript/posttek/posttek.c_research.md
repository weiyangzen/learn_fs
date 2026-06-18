# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/posttek/posttek.c

Purpose: Implements `posttek`, a Tektronix 4014 stream to PostScript translator. It emits DSC comments, copies a PostScript prologue, translates Tektronix alpha/vector/point modes, and handles multi-page output.

Key behavior:
- `main` initializes signals, writes the PostScript header/prologue, parses options, processes input files/stdin, writes trailer/accounting.
- Options configure aspect ratio, copies, font, magnification, forms per page, page list, orientation, offsets, line width, included files, encoding, request passthrough, debug, and fatal-error behavior.
- `statemachine` drives modes: `RESET`, `ALPHA`, `GIN`, `GRAPH`, `POINT`, `SPECIALPOINT`, `INCREMENTAL`, `EXIT`.
- `alpha`, `graph`, `point`, and `incremental` translate Tektronix character, vector, point, and incremental plot encodings into PostScript operators.
- `control` and `esc` implement Tektronix control/escape handling, including font size, graphics mode, special point mode, formfeed, GIN, line style, and defocused line width.
- `formfeed`, `redirect`, and page-list helpers integrate page selection with DSC page accounting.

Dependencies and integration:
- Uses `comments.h`, `gen.h`, `path.h`, `ext.h`, and `posttek.h`.
- Requires prologue procedures such as `setup`, `pagesetup`, `v`, `t`, `p`, `i`, `l`, `w`, `f`, and `done`.
- Shares common PostScript command-line conventions with other Plan 9 postscript tools.

Risks and notes:
- K&R-style C and global state make reentrancy impossible.
- `redirect` sends unselected pages to `/dev/null`, but page state still advances.
- Graph decoding depends on retained static address fields and must preserve Tektronix byte ordering exactly.
- Uses `/dev/null`, stdio, and legacy `signal` behavior.
