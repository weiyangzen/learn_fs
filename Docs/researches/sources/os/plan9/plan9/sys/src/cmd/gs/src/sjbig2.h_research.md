# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjbig2.h

Header for the JBIG2Decode stream filter.

Key contents:
- Defines `stream_jbig2decode_state` with optional global context, decoder context, current image, image output offset, and error code.
- Declares helpers for creating and attaching a global context.
- Declares GC structure macro and `s_jbig2decode_template`.

Notable dependencies:
- External `jbig2.h`.
- `scommon.h` stream-state definitions.

Research notes:
- The global context pointer is not owned by the stream state; the implementation comments say interpreter code frees it.
