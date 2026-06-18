# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_callmsg.c

Read completely: 212 lines.

Implements `xdr_callmsg()`, the XDR encoder/decoder for RPC call messages. It has optimized inline paths for encoding and decoding fixed fields plus credential/verifier auth blobs, and a fallback path using normal XDR primitives.

The function enforces `CALL` direction and `RPC_MSG_VERSION`, rejects auth bodies larger than `MAX_AUTH_BYTES`, and allocates `oa_base` with `mem_alloc()` on decode when the caller did not provide storage. It handles both credential and verifier opaque auth sections.

This is a critical wire-format routine used by service transports such as datagram and raw RPC. Correct caller initialization of `oa_base` matters: service dispatch uses stack credential storage, while generic decode can allocate.
