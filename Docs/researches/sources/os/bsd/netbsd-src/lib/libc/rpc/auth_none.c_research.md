# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/auth_none.c

Read completely: 158 lines.

This file implements AUTH_NONE client authentication through `authnone_create` and static auth ops.

Key behavior: lazily allocates one process-global `authnone_private`, initializes credential and verifier to `_null_auth`, pre-marshals both opaque auth structures into a fixed 20-byte buffer, and returns the embedded `AUTH`. Marshal writes the cached bytes; validate always succeeds; refresh always fails; destroy is a no-op.

Important interactions: default auth for raw, datagram, and virtual-circuit clients.

Security/reliability notes: global cached state is simple but not strongly synchronized here. AUTH_NONE provides no authentication and should only be considered protocol compatibility.
