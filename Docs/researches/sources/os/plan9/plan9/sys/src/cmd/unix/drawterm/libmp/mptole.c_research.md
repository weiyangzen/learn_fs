# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptole.c

Implements `mptole(mpint *b, uchar *p, uint n, uchar **pp)`, exporting an `mpint` magnitude to a little-endian byte array. It includes `os.h`, `<mp.h>`, and `dat.h`.

When no output buffer is supplied, it allocates `(b->top+1)*Dbytes`; when `pp` is non-nil it returns the selected buffer. The function zero-fills the whole output span, writes complete low limbs byte by byte, and trims high zero bytes from the most significant limb.

Return value is bytes written or `-1` for allocation/buffer failure. Notable quirk: for `b->top == 0`, it returns `0` if at least one byte of space exists, unlike `mptobe`, which returns `1` for zero. The sign is not serialized.
