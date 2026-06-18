# sources/user-network-fs/samba/source3/rpc_server/rpc_pipes.h

## Purpose
`rpc_pipes.h` defines source3 compatibility state for DCE/RPC named-pipe handlers and declares policy-handle helpers used by generated RPC server stubs. It is the bridge between older source3 pipe-server code and the common `dcesrv` call model.

## Important APIs, Types, And Functions
`struct pipes_struct` carries the transport, messaging context, current fault code, per-PDU memory context, and `dcesrv_call_state`. Declared helpers include `check_open_pipes`, `num_pipe_handles`, `create_policy_hnd`, `_find_policy_by_hnd`, `find_policy_by_hnd`, `close_policy_hnd`, and `pipe_access_check`. The `DCESRV_COMPAT_NOT_USED_ON_WIRE` macro generates an operation stub that faults with `DCERPC_FAULT_OP_RNG_ERROR`.

## Control Flow
The header has no implementation flow, but generated or hand-written RPC operations receive a `pipes_struct`, use it to access current call state and policy handles, and can set `fault_state` for protocol-level failures.

## State And Persistence
Policy handles and per-call memory are runtime state only. The `mem_ctx` field is explicitly per-PDU and must not be used for long-lived pipe state.

## Dependencies And Integration Points
The header depends on source3 DCE/RPC declarations and is included by `rpc_server.h`, service implementations, and compatibility wrappers. It connects generated server stubs to Samba messaging and dcesrv call state.

## Risks And Test Signals
Risks include using per-PDU memory for persistent state, mismatched policy-handle types, and accidentally exposing compatibility stubs on the wire. Test signals are policy handle create/find/close tests, access-check behavior, and RPC operation fault mapping.
