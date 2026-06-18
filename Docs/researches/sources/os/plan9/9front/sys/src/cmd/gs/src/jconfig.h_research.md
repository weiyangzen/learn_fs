# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jconfig.h

Concatenated Ghostscript configuration header for IJG JPEG compilation, combining `stdpn.h`, `stdpre.h`, and `gsjconf.h` style content. It defines deprecated `P0` through `P16` prototype macros, compiler/platform compatibility flags, inline handling, discard macros, alignment workarounds, type aliases, Boolean definitions, pointer comparison macros, min/max, rounding macros, `floatp`, `BEGIN`/`END`, client-name strings, `public`/`private`, and exit status macros.

The IJG section includes `arch.h`, maps Ghostscript prototype support to IJG `HAVE_PROTOTYPES`, declares unsigned char/short support, optional standard headers, far-pointer and short-name settings, allocation chunk limits for small `int` platforms, and JPEG internal right-shift behavior.

This header is portability glue for building IJG code inside Ghostscript’s cross-platform build system.
