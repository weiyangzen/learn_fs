# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_float.c

This file implements XDR serialization for `float` and `double`, exported as `xdr_float` and `xdr_double` with weak aliases for libc namespace handling.

For non-VAX targets it assumes IEEE floating point and serializes raw IEEE bits through `XDR_PUTINT32`/`XDR_GETINT32`. `xdr_float` is one 32-bit word. `xdr_double` is two 32-bit words, with word order selected by byte order and a special old ARM FPA condition: big-endian or non-VFP ARM sends the first word first, while little-endian sends the high word first to match XDR network representation.

For VAX targets the file defines bitfield layouts for VAX and IEEE single/double values. Encode paths translate VAX exponent/mantissa/sign into IEEE-style fields, with limit tables for max/min edge encodings. Decode paths perform the inverse translation and copy the resulting VAX representation into the destination.

`XDR_FREE` is a no-op for both functions, returning `TRUE`.

Dependencies are the generic RPC XDR interface in `<rpc/xdr.h>`, machine endian definitions for IEEE targets, and VAX-specific bitfield assumptions when `__vax__` is defined.

Research notes and risks:
- The IEEE path type-puns `float *` and `double *` through `int32_t *`; this is traditional RPC libc code but sensitive to aliasing/alignment assumptions.
- VAX support relies on implementation-defined bitfield layout.
- Floating NaN payload/signaling behavior is not normalized on IEEE targets; the raw representation is transported.
