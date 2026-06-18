# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zutil.h

Defines internal zlib configuration, constants, diagnostics, memory helpers, and target portability macros.

Key points:
- Marks itself as internal and includes `zlib.h` with `ZLIB_INTERNAL`.
- Defines internal aliases `uch`, `ush`, `ulg`, `local`, and error helpers `ERR_MSG` and `ERR_RETURN`.
- Sets common compression constants:
  - `DEF_WBITS`
  - `DEF_MEM_LEVEL`
  - block types `STORED_BLOCK`, `STATIC_TREES`, `DYN_TREES`
  - match lengths `MIN_MATCH`, `MAX_MATCH`
  - zlib preset dictionary flag
- Maps operating-system codes for gzip headers across DOS, Amiga, VMS, Atari, OS/2, Mac, TOPS20, Win32, Prime, BeOS, RISC OS, and default Unix.
- Provides `F_OPEN` abstraction and `fdopen` compatibility shims.
- Detects `vsnprintf`, `strerror`, and memcpy availability.
- Maps `zmemcpy`, `zmemcmp`, and `zmemzero` to libc or fallback functions.
- Defines debug macros `Assert`, `Trace`, `Tracev`, `Tracevv`, `Tracec`, `Tracecv`.
- Declares `zcalloc` and `zcfree`, and wraps stream alloc/free through `ZALLOC`, `ZFREE`, and `TRY_FREE`.

Dependencies and interactions:
- Used by zlib implementation files, not applications.
- Depends on `zconf.h` via `zlib.h`.
- Paired with `zutil.c`.

Research relevance:
- This is the internal portability contract for the vendored compression library and explains how the same source is configured for Plan 9’s Ghostscript build.
