# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sjpx.h

Defines state for the `JPXDecode` stream.

Key points:
- Includes JasPer headers and `scommon.h`.
- `stream_jpxd_state` stores JasPer image/stream pointers, output offset, non-GC memory, compressed-data buffer, buffer size, and fill count.
- Comments document the design limitation: compressed input is spooled fully before passing to JasPer.
- Defines a simple GC descriptor and exports `s_jpxd_template`.

Research relevance:
- Header-level contract for the JPEG 2000 external decoder stream.
