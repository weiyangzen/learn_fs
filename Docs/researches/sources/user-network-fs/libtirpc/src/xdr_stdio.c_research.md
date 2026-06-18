# sources/user-network-fs/libtirpc/src/xdr_stdio.c

Purpose: `xdr_stdio.c` implements an XDR stream backend over a C `FILE *`.

Important APIs, types, and functions: `xdrstdio_create` initializes the stream. Internal ops implement get/put long, get/put bytes, get/set position via `ftell`/`fseek`, no inline support, and destroy via `fflush`.

Control flow: Creation stores the `FILE *` in `x_private`. Reads use `fread` to obtain network-order 32-bit words or byte blocks. Writes range-check `long` values on LP64, convert through `htonl`, and use `fwrite`. Destroy flushes but deliberately does not close the underlying file.

State and persistence behavior: State is primarily in the stdio stream's file offset and buffers. The XDR object does not own the `FILE *`, and no heap storage is allocated by this backend.

Dependencies and integration points: It depends on stdio, `<arpa/inet.h>`, and generic XDR APIs. It is suitable for file-backed XDR payloads and compatibility code that serializes RPC structures to streams.

Risks: `xdrstdio_getpos` truncates `ftell` to `u_int`; large files are not safely represented. Inline operations always return null, so callers must support non-inline fallback. Destroy only flushes, leaving lifecycle and error handling for close to the caller. LP64 `putlong` rejects values outside signed 32-bit/unsigned 32-bit bounds, which may differ from other backends' casts.

Test signals: Tests should cover read/write round trips, zero-length byte transfers, failed short reads/writes, seek positioning, large-offset truncation expectations, flush-on-destroy, and LP64 range rejection.
