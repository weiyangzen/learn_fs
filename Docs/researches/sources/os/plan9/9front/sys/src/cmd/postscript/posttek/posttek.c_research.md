# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/posttek/posttek.c

Tektronix 4014-to-PostScript translator. It implements a terminal-state emulator for alpha, graph, point, special point, GIN, and incremental plot modes, emitting PostScript calls defined by the `posttek` prologue.

Key behavior:
- Emits DSC header/prologue/setup, parses layout/font/accounting options, processes each input file through `statemachine`, then writes trailer/accounting.
- `alpha` prints text using Tek character size tables and wraps/margins.
- `graph` decodes Tek 4014 packed coordinate bytes into vectors.
- `point` and `incremental` handle point plotting/intensity and relative pen movement.
- `control` and `esc` implement Tek control/escape mode changes, line styles, defocus/line width, formfeed, and font size commands.
- `formfeed` closes current page, filters pages with `redirect`, and initializes the next page.

Integration points:
- Uses shared PostScript DSC/request helpers and path constants.
- `posttek.h` supplies control-code constants, state IDs, font maps, intensity table, style arrays, and coordinate limits.
- Requires prologue procedures `setup`, `pagesetup`, `v`, `t`, `p`, `i`, `l`, `w`, `f`, and `done`.

Risks:
- Parser relies on legacy terminal byte semantics; malformed streams can cause odd state transitions.
- Fixed stack batching limit for vectors (`points > 100`) is manual and prologue-dependent.
- Old-style declarations and global state limit reentrancy and portability.
