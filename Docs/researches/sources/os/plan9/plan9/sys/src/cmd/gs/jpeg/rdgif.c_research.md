# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdgif.c

This file is a stub GIF input module for `cjpeg`, compiled only if `GIF_SUPPORTED` is defined.

The original GIF reader was removed from the IJG distribution to avoid LZW patent issues. The only exported function, `jinit_read_gif()`, prints an unsupported message to stderr, exits with `EXIT_FAILURE`, and returns `NULL` only to satisfy the compiler.

It includes `cdjpeg.h` for application declarations but performs no image parsing. GIF palette reading for `djpeg -map` is separate and remains in `rdcolmap.c` because it does not decode LZW image data.
