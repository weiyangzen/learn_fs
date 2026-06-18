# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/cfonts.mak

This makefile generates and compiles PostScript Type 1 fonts into C for Ghostscript.

Core responsibilities:
- Defines `CFONTS_MAK`, generated/object directory aliases, compile command variables, and the `font2c` invocation.
- Builds a temporary Ghostscript command file `font2c.tmp` that runs `font2c.ps` with `BUILD_TIME_GS`.
- Provides aggregate targets for `fonts_standard_c`, `fonts_standard_o`, `fonts_free_c`, and `fonts_free_o`.

Font sets:
- Standard 35 fonts: Avant Garde, Bookman, Courier, Helvetica, New Century Schoolbook, Palatino, Times Roman, Symbol, Zapf Chancery, and Zapf Dingbats.
- Additional/free fonts: Bitstream Charter, Cyrillic, Kana, and Utopia.

Build pattern:
- Each font target first invokes `FONT2C` to generate a `.c` file with a short internal name.
- The corresponding object target compiles the generated `.c` file against `ccfont.h`.

Filesystem relevance is build-time only: reads font resources through Ghostscript and emits generated C/object files.
