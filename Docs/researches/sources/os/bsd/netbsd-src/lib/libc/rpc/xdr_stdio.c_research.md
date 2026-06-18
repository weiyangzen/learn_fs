# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_stdio.c

This file implements an XDR backend over a standard C `FILE *`, exported as `xdrstdio_create`.

`xdrstdio_create` initializes the caller-provided `XDR` object with operation mode, a static stdio ops vector, and the `FILE *` in `x_private`. The ops serialize and deserialize 32-bit longs using `htonl`/`ntohl` around `fwrite`/`fread`, copy counted bytes with stdio calls, report position through `ftell`, seek through `fseek`, and flush the stream on destroy.

Inline access is deliberately unsupported and always returns NULL because stdio buffering cannot easily guarantee alignment and contiguous availability for XDR inline macros.

Research notes and risks:
- `xdrstdio_destroy` flushes but does not close the underlying file.
- Position is returned as `u_int`, so large stream offsets can truncate.
- Byte reads/writes use one `fread`/`fwrite` item of length `len`; partial I/O returns failure.
