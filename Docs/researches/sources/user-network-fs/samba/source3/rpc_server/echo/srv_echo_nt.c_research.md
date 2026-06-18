# sources/user-network-fs/samba/source3/rpc_server/echo/srv_echo_nt.c

Purpose: simple RPC echo pipe implementation used for DCERPC plumbing tests and basic server behavior validation.

Important APIs/types/functions: `_echo_AddOne`, `_echo_EchoData`, `_echo_SinkData`, `_echo_SourceData`, `_echo_TestSleep`, and several unsupported test calls that set `DCERPC_FAULT_OP_RNG_ERROR`.

Control flow: `_echo_AddOne` increments a scalar. `_echo_EchoData` allocates output data in `p->mem_ctx` and copies input bytes unless length is zero. `_echo_SinkData` discards input. `_echo_SourceData` returns a deterministic byte sequence `i & 0xff` of requested length. `_echo_TestSleep` sleeps synchronously for the requested seconds and returns zero. Other methods are deliberately fault stubs.

State/persistence behavior: stateless except for synchronous sleep and per-call talloc allocations. It does not persist data or maintain handles.

Dependencies/integration: depends on generated `ndr_echo` structures, RPC pipe memory context handling, Samba debug logging, and `smb_msleep`.

Risks/test signals: useful for testing NDR array marshalling, zero-length pointer behavior, RPC fault mapping, server blocking behavior during sleep, and memory allocation for arbitrary requested lengths. It is intentionally small but can reveal transport, generated boilerplate, and pipe dispatch regressions.
