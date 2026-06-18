# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/__rpc_getxid.c

Read completely: 60 lines.

This file implements `__rpc_getxid`, returning a 32-bit RPC transaction ID from a static `randomid_t` context.

Key behavior: lazily creates the random ID generator with `randomid_new(32, RANDOMID_TIMEO_DEFAULT)` and aborts if allocation/initialization fails; each call returns `randomid(ctx)`.

Important interactions: used by RPC client constructors and broadcast code to seed call message XIDs.

Security/reliability notes: the static context is shared; thread-safety depends on `randomid` internals. Initialization failure terminates the process via `abort()`.
