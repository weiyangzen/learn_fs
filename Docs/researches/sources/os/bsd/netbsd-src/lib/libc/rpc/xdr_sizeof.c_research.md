# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_sizeof.c

This file implements `xdr_sizeof`, a measuring XDR backend that runs an XDR encode procedure without producing a real serialized buffer and returns the number of bytes that would be emitted.

It defines a local `xdr_ops` vector where put operations increment `x_handy`: `x_putlong` adds one XDR unit, and `x_putbytes` adds the requested byte count. `x_inline` supports encode-only inline requests by allocating or reusing a scratch buffer large enough for the inline region, incrementing `x_handy`, and returning that scratch memory. Get operations are harmless stubs returning false/null, because `xdr_sizeof` only runs in `XDR_ENCODE` mode.

`xdr_sizeof` initializes a stack `XDR`, installs these ops, calls the supplied `xdrproc_t`, frees any scratch inline buffer, and returns the counted size on success or 0 on failure.

Research notes and risks:
- Size counting depends on the supplied XDR procedure taking the normal encode path and honoring op return values.
- The inline scratch buffer exists only to satisfy encode procedures that write through `XDR_INLINE`; its contents are discarded.
- `x_base` is used as a stored allocation size via pointer/integer casts, which is compact but non-obvious.
