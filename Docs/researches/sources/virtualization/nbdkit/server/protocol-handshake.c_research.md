# File Research: sources/virtualization/nbdkit/server/protocol-handshake.c

This file selects oldstyle versus newstyle handshake under the global request lock. `protocol_handshake` calls `protocol_handshake_oldstyle` when `newstyle` is false and `protocol_handshake_newstyle` otherwise, then releases the lock.

It also provides `protocol_common_open`, the shared late-open path used by both handshake styles. The function opens the backend, prepares filters, obtains export size, rejects negative sizes, and computes NBD export flags by probing write, zero, fast-zero, trim, FUA, flush, rotational, multi-conn, cache, and extents capabilities.

The computed flags include readonly, write-zeroes, fast-zero, trim, FUA, flush, rotational, multi-conn, cache, and DF support when structured replies were negotiated. Multi-conn is advertised only if the backend supports it and the effective thread model allows more than serialized connections. Extents capability is deliberately probed even though it is not directly advertised in eflags, priming backend capability caches for later block-status handling.
