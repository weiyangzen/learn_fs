# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibx.h

Public zlib stream state definition.

Key points:
- Forward-declares `zlib_dynamic_state_t`.
- Defines `stream_zlib_state` with common stream state plus:
  - `windowBits`
  - `no_wrapper`
  - compression `level`
  - `method`
  - `memLevel`
  - `strategy`
  - dynamic state pointer
- Defines the public GC descriptor macro for zlib stream state.
- Declares `s_zlibD_template` and `s_zlibE_template`.
- Declares shared `s_zlib_set_defaults`.

Dependencies and interactions:
- Included by zlib encoder/decoder users and `szlibxx.h`.

Research relevance:
- Public state contract for Ghostscript zlib filters.
