# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ckconfig.c

Manual configuration helper that compiles and runs to generate `jconfig.h` for IJG builds on systems without autoconf.

Key behavior:
- Starts with editable `#define`/`#undef` probes for standard headers, BSD strings, `sys/types.h`, special size_t includes, prototypes, `unsigned char`, `unsigned short`, `void`, `const`, incomplete types, and short external names.
- Provides small test functions to exercise prototypes, method-pointer declarations, `void *`, function pointers returning void, const behavior, and duplicate external-name handling.
- `is_char_signed` detects signedness and warns if `char` does not appear to be 8 bits.
- `is_shifting_signed` detects whether right shift of negative `long` values is arithmetic or logical.
- `main` writes `jconfig.h` with detected/configured macros, internal JPEG right-shift setting, and application feature defaults for BMP/GIF/PPM/Targa support, disabled RLE, Unix-style command line, signal catcher, binary mode, and optional progress reporting.
- Prints user guidance about using `makefile.ansi` or `makefile.unix`.

Dependencies:
- Uses stdio plus optional stddef, stdlib, strings/string, sys/types, and a placeholder special include.
- Assumes the user may need to edit the file based on compiler errors before running it.

Research notes:
- This is a historical interactive portability probe, not an automatic robust configure system.
- The generated application feature defaults may need manual adjustment for the target platform.
- It writes directly to `jconfig.h` in the current directory.
