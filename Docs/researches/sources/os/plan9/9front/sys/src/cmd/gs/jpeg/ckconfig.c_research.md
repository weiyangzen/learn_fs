# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ckconfig.c

Manual configuration probe program for IJG JPEG builds.

Key points:
- Intended to be edited, compiled, and run on systems without Autoconf support to generate `jconfig.h`.
- Starts with optimistic defines for standard headers, prototypes, unsigned char/short, `void`, `const`, and complete incomplete-type support; comments instruct users to flip defines based on the first compiler error.
- Probes or exercises include `stddef.h`, `stdlib.h`, string vs BSD strings, `sys/types.h` for `size_t`, ANSI prototypes, method-pointer declarations, unsigned types, `void *`, function pointers returning void, `const`, incomplete structure pointers, and external-name length collisions.
- Runtime helpers test whether plain `char` is signed and whether right-shift of negative `long` is arithmetic or logical.
- `main` writes a generated `jconfig.h` with detected/assumed macros plus app-format defaults: BMP/GIF/PPM/Targa enabled, RLE disabled, two-file command line and signal catcher disabled, optional progress commented out.
- Prints post-run guidance choosing `makefile.ansi` or `makefile.unix` based on prototype support.

Dependencies and interactions:
- Alternative to the generated `configure` script for producing `jconfig.h`.
- The generated header drives conditional compilation in `jinclude.h`, `jmorecfg.h`, `cdjpeg.h`, memory managers, and application modules.

Risk notes:
- Because users are expected to edit the file between compile attempts, the output reflects manual decisions as much as automatic detection.
- The generated defaults are generic IJG defaults and may not match the 9front/Ghostscript build system if used directly.
- The runtime tests assume 8-bit `char` and 32-bit-relevant `long` behavior; nontraditional machines are warned as likely unsupported.
