# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md4.c

Implements MD4 hashing from Stinson’s description. It includes `os.h` and `<libsec.h>`.

The file defines MD4 rotation constants, a 48-entry round table, static `md4block`, `encode`, and `decode` helpers, and public `md4(uchar *p, ulong len, uchar *digest, MD4state *s)`. The state machine supports streaming: when `digest == nil`, partial input is retained in `s->buf`; when `digest` is supplied, the function pads, appends bit length, finalizes, writes the digest, and frees malloced state.

The block function processes 64-byte blocks over MD4’s three rounds and updates four state words. Output encoding is little-endian, matching MD4 convention.
