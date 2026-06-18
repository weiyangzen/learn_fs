# sources/user-network-fs/libtirpc/src/xdr_float.c

Purpose: `xdr_float.c` provides XDR filters for `float` and `double`, encoding IEEE floating point values in network byte order and preserving legacy VAX conversion code when built for VAX.

Important APIs, types, and functions: Public functions are `xdr_float` and `xdr_double`. The normal `IEEEFP` path uses `XDR_PUTINT32`/`XDR_GETINT32` over the in-memory representation. The VAX path defines bitfield layouts and limit tables for single and double conversion.

Control flow: `xdr_float` encodes or decodes one 32-bit word. `xdr_double` encodes or decodes two 32-bit words, swapping word order on little-endian hosts so the XDR stream remains big-endian IEEE representation. `XDR_FREE` is a no-op for both.

State and persistence behavior: The file maintains no mutable state. It reads and writes caller-owned floating point objects directly through integer pointers.

Dependencies and integration points: It depends on endian macros from `<endian.h>` or `<machine/endian.h>`, `rpc/types.h`, and `rpc/xdr.h`. Protocols with floating point fields delegate to these filters.

Risks: The implementation type-puns floats/doubles through `int32_t *`, which can trigger strict-aliasing or alignment concerns on some compilers/architectures. IEEE handling assumes host IEEE representation; non-IEEE platforms outside the VAX branch are not covered. NaN payload and signed-zero preservation depends on raw bit transport.

Test signals: Round-trip tests should cover normal values, infinities, NaNs, signed zero, big- and little-endian builds if available, and compiler sanitizer/strict-aliasing builds.
