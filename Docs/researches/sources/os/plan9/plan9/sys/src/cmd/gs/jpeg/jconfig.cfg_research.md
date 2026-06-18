# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jconfig.cfg

Template configuration file for IJG `jconfig.h` generation.

Key behavior:
- Undefines portability and compiler feature macros that a configure step may set, such as prototypes, unsigned char/short support, standard headers, BSD strings, far pointers, and short external names.
- Under `JPEG_INTERNALS`, provides internal configuration placeholders for unsigned right shift behavior, `INLINE`, default memory limits, and `mktemp` availability.
- Under `JPEG_CJPEG_DJPEG`, enables BMP, GIF, PPM, and Targa support while disabling Utah RLE, two-file command line mode, signal catching, binary-mode avoidance, and progress reports.

Dependencies:
- Intended to be edited or transformed by IJG configuration tooling and included indirectly as generated JPEG build configuration.

Notable risks:
- This is not runtime code; actual behavior depends on the generated/selected `jconfig.h` used by the build.
- The file reflects conservative defaults and may be superseded by Ghostscript/Plan 9 build glue elsewhere.
