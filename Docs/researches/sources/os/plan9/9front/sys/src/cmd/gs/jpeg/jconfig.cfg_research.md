# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jconfig.cfg

Autoconf template for generated `jconfig.h`.

Key points:
- Contains `#undef` placeholders for compiler/platform capabilities: prototypes, unsigned char/short, `void`, `const`, char signedness, standard headers, BSD strings, `sys/types.h`, far pointers, short external names, and incomplete-type behavior.
- Under `JPEG_INTERNALS`, configures right-shift behavior, `INLINE`, default memory limits, and `NO_MKTEMP`.
- Under `JPEG_CJPEG_DJPEG`, enables BMP/GIF/PPM/Targa sample-app support by default, leaves Utah RLE disabled, and controls two-file command line, signal catcher, binary-mode handling, and progress reports.

Dependencies and interactions:
- Consumed by the old `configure` script to produce `jconfig.h`.
- The resulting macros affect public headers, core library internals, memory managers, and command-line utilities.

Risk notes:
- This is a template, not a usable configuration header until processed.
- Feature defaults are command-line app defaults and may differ from the Plan 9/Ghostscript build’s effective configuration.
