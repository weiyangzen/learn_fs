# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTrace.cc

Purpose: implements binary-to-hex formatting for tracing.

Important APIs, types, and functions: `XrdOucTrace::bin2hex(char *inbuff, int dlen, char *buff)` converts up to 24 bytes into lower-case hex pairs with spaces after every four bytes and at the end. If no output buffer is supplied, it uses a static 56-byte buffer.

Control flow: the method clamps `dlen`, iterates input bytes, writes two hex chars per byte, adds spacing, null-terminates, and returns the static buffer pointer.

State and persistence: the only state is the function-static output buffer used when `buff` is null. That static buffer is overwritten on each call and is not thread-safe.

Dependencies and integration points: depends on `XrdOucTrace.hh`. It supports trace log formatting alongside `XrdSysError` trace begin/end methods from the header.

Risks and test signals: when a caller supplies `buff`, the function still returns `xbuff` rather than the supplied buffer, which appears incorrect. Callers must also size custom buffers for the formatted output. Tests should cover explicit-buffer return value, 0/1/4/24/over-24 byte lengths, signed-char inputs, and concurrent use of the static buffer.
