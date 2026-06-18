# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/smd5.c

Implements the `MD5Encode` stream filter.

Key points:
- Initializes an MD5 state in `s_MD5E_init`.
- Processing consumes all available input with `md5_append`.
- On final input, emits the 16-byte digest if output space is available, otherwise asks for more output space.
- `s_MD5E_make_stream` allocates a stream and state, initializes the filter over a caller-provided digest buffer, and returns the stream.

Dependencies and interactions:
- Uses `md5.h` state functions through `smd5.h`.

Research relevance:
- Digest-producing stream filter used where Ghostscript wants to hash streamed data without separate buffering.
