# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/cfonts.mak

This makefile builds PostScript Type 1 fonts into generated C sources and object files for Ghostscript.

Key responsibilities:
- Defines compiled-font build directories and compiler invocations based on `PSSRCDIR`, `PSGENDIR`, and `PSOBJDIR`.
- Creates `font2c.tmp`, an argument file used to invoke Ghostscript with `font2c.ps`.
- Defines `FONT2C=$(BUILD_TIME_GS) @$(F2CTMP)`.
- Provides aggregate targets for two font sets:
  - `fonts_standard_c` and `fonts_standard_o`
  - `fonts_free_c` and `fonts_free_o`
- Generates C files and object files for the standard 35 PostScript fonts and additional free fonts.

Font groups covered:
- Standard fonts: Avant Garde, Bookman, Courier, Helvetica including Narrow variants, New Century Schoolbook, Palatino, Times Roman, Symbol, Zapf Chancery, and Zapf Dingbats.
- Additional fonts: Bitstream Charter, Cyrillic, Kana, and Utopia.

Important build relationships:
- Generated C files depend on `F2CDEP`, which includes `MAKEFILE` and the generated `font2c.tmp`.
- Object rules compile generated `.c` files with `$(CFCC)` and depend on `$(CCFONT)`.
- Uses short generated names such as `0agk.c`, `0hvr.c`, `0tmr.c`, `bchr.c`, `fcyr.c`, and `putr.c`.

Notable implementation details:
- This is build-generation logic, not runtime font logic.
- Requires a build-time Ghostscript executable.
- No filesystem implementation logic beyond generating and compiling files.

Research classification: Ghostscript compiled-font build recipe.
