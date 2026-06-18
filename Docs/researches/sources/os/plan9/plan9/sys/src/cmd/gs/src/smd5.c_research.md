# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/smd5.c

MD5Encode stream filter.

Key behavior:
- `s_MD5E_init` initializes the MD5 state.
- `s_MD5E_process` consumes all input into `md5_append`; when `last` is true and 16 output bytes are available, emits the digest with `md5_finish` and returns `EOFC`.
- `s_MD5E_make_stream` allocates a stream and state, initializes an MD5 filter over a caller-supplied digest buffer, and returns the stream.

Notable dependencies:
- MD5 implementation from `md5.h`.
- Ghostscript stream allocation and filter initialization APIs.

Research notes:
- The filter emits no output until close/final input.
- `s_MD5E_make_stream` cleans up both stream and state on initialization failure.
