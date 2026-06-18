# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jconfig.h

Purpose: generated/combined configuration header for Independent JPEG Group code in the Ghostscript build.

Contents:
- Starts with deprecated `stdpn.h`-style `P0` through `P16` prototype macros for older Ghostscript/IJG compatibility.
- Includes Ghostscript `stdpre.h` platform abstraction: compiler feature detection, prototype/inline handling, standard integer aliases, bool definitions, pointer comparison macros, rounding/count/offset helpers, `private`/`public` conventions, `client_name_t`, and exit status definitions.
- Ends with the IJG `gsjconf.h` configuration body, including `arch.h`, prototype support, unsigned char/short support, optional standard headers under `__STDC__`, disabled BSD/sys/types/far-pointer/short-name workarounds, small-int `MAX_ALLOC_CHUNK`, and JPEG-internal right-shift behavior based on `ARCH_ARITH_RSHIFT`.

Research notes:
- The comments explain that `stdpre.h` is concatenated into this file because of the IJG library build directory layout.
- This file is compile-time portability and third-party JPEG configuration, not Ghostscript interpreter runtime logic.
