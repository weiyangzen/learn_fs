# sources/user-network-fs/libtirpc/src/xdr_mem.c

Purpose: `xdr_mem.c` implements an XDR stream backend over a caller-provided memory buffer.

Important APIs, types, and functions: `xdrmem_create` initializes the stream and selects aligned or unaligned ops. Operation implementations include get/put long, get/put bytes, get/set position, inline access for aligned buffers, and a no-op destroy function.

Control flow: Creation stores the operation mode, base pointer, current pointer, and remaining byte count. Get/put long checks at least four bytes remain, converts via `ntohl`/`htonl`, advances the pointer, and decrements `x_handy`. Byte get/put uses `memmove`. Positioning computes offsets from `x_base` and refuses seeks beyond the original end. Inline access returns a direct pointer only for aligned streams with enough remaining bytes.

State and persistence behavior: All state is embedded in the caller-provided `XDR` object and references the caller-owned buffer. Destroy does not free or flush anything.

Dependencies and integration points: It depends on `<netinet/in.h>` byte order helpers and the generic XDR ops table. It is used for in-memory pre-serialization, raw RPC, testing, auth marshaling, and generated protocol encode/decode against fixed buffers.

Risks: Position values are `u_int`; comments note this is insufficient for 64-bit pointer-sized buffers. Aligned paths cast buffer memory to `u_int32_t *`, so creation's alignment detection is important. `xdrmem_setpos` computes bounds from current pointer plus remaining bytes, preserving the original end but relying on valid existing stream state.

Test signals: Tests should cover aligned and unaligned buffers, exact-boundary reads/writes, failed overrun, seek forward/backward within bounds, failed seek beyond end, and inline availability only for aligned streams.
