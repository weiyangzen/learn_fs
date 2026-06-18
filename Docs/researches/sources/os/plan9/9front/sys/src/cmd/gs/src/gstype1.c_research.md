# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype1.c

Implements the Adobe Type 1 charstring interpreter.

Key behavior:
- `gs_type1_interpret` continues or starts interpretation for a `gs_type1_state`, optional glyph data, and othersubr callback index.
- Initializes the Type 1 hinter, maps font/CTM/subpixel data, and passes Type 1 font data into hinting before interpretation.
- Maintains operand and instruction stacks, decryption state, call depth, and current fixed-point origin.
- Decodes Type 1 charstring numbers in one-, two-, and four-byte forms, including a special large-number division workaround.
- Handles subroutine calls/returns through font `subr_data` callbacks and frees returned glyph data.
- Dispatches Type 1/Type 2-shared drawing commands to the hinter: stems, moves, lines, curves, closepath, endchar, and current point update.
- Implements `hsbw` and `sbw`, returning `type1_result_sbw` to allow client intervention after sidebearing/width setup.
- Handles `seac`, including accent recursion and sidebearing adjustment for a documented Fontographer workaround.
- Handles Type 1 escaped commands including dotsection, stem3, div, callothersubr, pop, and setcurrentpoint.
- Implements known Flex and Multiple Master blend othersubrs internally; unknown othersubrs are passed to client callbacks with copied operand values and return `type1_result_callothersubr`.

Dependencies:
- Uses Type 1 font data, glyph data, path/imager state, fixed arithmetic, font matrix mapping, Type 1 hinting (`gxhintn.h`), and callback procedures from the font data.

Research notes:
- The interpreter is resumable: it stores instruction pointer, decryption state, operand stack count, and call stack count when returning for client intervention.
- Many invalid or unsupported opcodes return `invalidfont`, matching PostScript font error semantics.
