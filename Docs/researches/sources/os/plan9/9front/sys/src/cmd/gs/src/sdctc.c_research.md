# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sdctc.c

Common DCT encode/decode support. It declares the public GC descriptor for `stream_DCT_state` and implements `s_DCT_set_defaults`.

Defaults set JPEG allocation memory to Ghostscript’s non-GC memory, clear the libjpeg data pointer, set `ColorTransform` to unspecified, `QFactor` to `1.0`, and clear marker data.

Dependencies include `jpeglib_.h`, Ghostscript memory allocation headers, `strimpl.h`, and `sdct.h`.

This is shared JPEG stream initialization support.
