# sources/user-network-fs/libtirpc/tirpc/rpc/raw.h

Purpose: `raw.h` declares the shared in-memory communication buffer used by raw RPC client/server transports for testing and local performance paths.

Important APIs, types, and functions: The only exported symbol is `char *__rpc_rawcombuf`.

Control flow: Raw client and service implementations use the common buffer instead of sockets to pass encoded RPC messages in process.

State and persistence behavior: `__rpc_rawcombuf` is global mutable process state. Its allocation and lifetime are implementation-defined outside this header.

Dependencies and integration points: It is used by `clnt_raw_create`/`clntraw_create` and `svc_raw_create`/`svcraw_create`.

Risks: A single global buffer is inherently not thread-safe or reentrant across simultaneous raw RPC calls. It is suitable for tests and benchmarks, not isolated multi-client state.

Test signals: Tests should cover raw client/server round trips, buffer allocation, repeated calls, and expected non-thread-safe behavior or locking if implementations add it.
