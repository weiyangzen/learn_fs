# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptobe.c

Implements `mptobe(mpint *b, uchar *p, uint n, uchar **pp)`, exporting a Plan 9 `mpint` magnitude to a big-endian byte array. It includes `os.h`, `<mp.h>`, and `dat.h`, and operates directly on `mpint->top`, `mpint->p[]`, `Dbytes`, and `Dbits`.

The function allocates `(b->top+1)*Dbytes` when `p == nil`, optionally returns the buffer via `pp`, zero-fills the caller/allocation buffer, and suppresses leading zero bytes while scanning limbs from most significant to least significant. It returns the number of bytes written, or `-1` on allocation failure or insufficient caller-supplied space.

Important behavior: zero is special-cased to require at least one output byte and returns `1`, while nonzero values also guarantee at least one byte. The sign is not encoded; this is a magnitude serialization helper for higher-level crypto/integer code.
