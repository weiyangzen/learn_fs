# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readv210.c

Decoder for single-frame QuickTime `v210` 10-bit YUV video stills. It infers dimensions and per-line chunk size by comparing file size against `/lib/video.specs`.

`BreadV210` unpacks 32-bit little-endian groups into 10-bit Cb/Y/Cr/Y samples, stores an intermediate multiplexed frame, then converts YCbCr to planar `CRGB` bytes. It selects conversion constants for PAL-like 625-line versus 525/HD cases.

Only `CYCbCr` input mode is accepted by the API despite returning RGB channels. Missing video specs or unknown file sizes produce recoverable `werrstr`/`nil` failures.
