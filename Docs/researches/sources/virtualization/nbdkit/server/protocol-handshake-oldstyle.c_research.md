# File Research: sources/virtualization/nbdkit/server/protocol-handshake-oldstyle.c

This file implements the legacy NBD oldstyle handshake. Oldstyle has no option phase, so the server immediately opens the default export name `""` through `protocol_common_open`, computes export flags, and sends `NBD_MAGIC`, `NBD_OLD_VERSION`, export size, global flags, and export flags in a zero-padded oldstyle handshake structure.

Because oldstyle cannot report structured negotiation errors to the client, any `.open`, `.prepare`, `.get_size`, or capability failure causes a disconnect. The code asserts `tls != 2`, because forced TLS is filtered earlier and cannot be negotiated through oldstyle.
