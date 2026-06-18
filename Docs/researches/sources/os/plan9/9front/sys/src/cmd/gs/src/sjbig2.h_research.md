# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sjbig2.h

Defines state and API declarations for `JBIG2Decode`.

Key points:
- Includes `<jbig2.h>` and `scommon.h`.
- `stream_jbig2decode_state` stores optional globals, decode context, current page image, output offset, and error code.
- Declares helpers for creating and attaching global contexts.
- Defines a simple GC descriptor and exports `s_jbig2decode_template`.

Research relevance:
- Header-level contract for the JBIG2 external decoder stream.
