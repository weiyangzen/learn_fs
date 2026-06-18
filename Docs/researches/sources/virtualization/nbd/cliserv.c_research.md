# File Research: sources/virtualization/nbd/cliserv.c

Shared client/server support implementation.

It defines protocol magic constants for classic client/server negotiation, option negotiation, and option replies. It provides `set_nonblocking()`, TCP socket tuning through `TCP_NODELAY`, shared error reporting helpers, fatal exit wrappers, logging initialization, endian conversion for 64-bit network order, and full-length `readit()`/`writeit()` loops.

`readit()` and `writeit()` keep reading/writing until the requested length is transferred, treating `EAGAIN` as retryable and other errors as fatal/nonfatal diagnostics depending on caller path.

Pointer arithmetic on `void *` appears in the read/write loops, relying on compiler extension behavior.
