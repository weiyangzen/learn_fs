# sources/user-network-fs/samba/source4/rpc_server/echo/rpc_echo.c

## Purpose
`rpc_echo.c` implements Samba's test/demo DCE/RPC echo endpoint. It provides simple IDL methods that exercise scalar returns, array allocation, pointer handling, union selection, enum marshalling, nested structures, double pointers, and asynchronous reply support.

## Important APIs, Types, and Functions
- `dcesrv_interface_rpcecho_bind()` delegates bind authorization to `dcesrv_interface_bind_allow_connect()`.
- `dcesrv_echo_AddOne()` returns the input integer plus one.
- `dcesrv_echo_EchoData()` copies an input byte buffer to an output buffer using `talloc_memdup()`.
- `dcesrv_echo_SinkData()` accepts data and discards it.
- `dcesrv_echo_SourceData()` allocates `len` bytes and fills them with increasing byte values.
- `dcesrv_echo_TestCall()` duplicates a string.
- `dcesrv_echo_TestCall2()` allocates a union and fills different arms based on request level.
- `dcesrv_echo_TestEnum()`, `dcesrv_echo_TestSurrounding()`, and `dcesrv_echo_TestDoublePointer()` cover enum, nested pointer, and triple-dereference cases.
- `dcesrv_echo_TestSleep()` either blocks with `sleep()` or schedules a tevent timer and returns asynchronously, depending on `DCESRV_CALL_STATE_FLAG_MAY_ASYNC`.

## Control Flow
Most calls are direct request-to-response transformations. The server binds without special checks. Data-returning functions allocate outputs on the RPC memory context and return `NT_STATUS_NO_MEMORY` when allocation fails. `TestCall2` switches on `r->in.level` and returns `NT_STATUS_INVALID_LEVEL` for unknown union arms.

`TestSleep` is the only stateful control path. If async replies are not permitted, it sleeps synchronously for the requested number of seconds and returns that value. If async is allowed, it allocates `echo_TestSleep_private`, stores the call state and request pointer, schedules `echo_TestSleep_handler()` on the call's event context, marks the call with `DCESRV_CALL_STATE_FLAG_ASYNC`, and returns zero immediately. The timer later writes `r->out.result` and calls `dcesrv_async_reply()`.

## State and Persistence Behavior
The endpoint has no durable state. Per-call allocations are attached to `mem_ctx`. Async sleep state is held in talloc memory owned by the request context until the timer fires. No database, file, or global state is modified.

## Dependencies and Integration Points
The file integrates with the generated echo NDR server stubs via `#include "librpc/gen_ndr/ndr_echo_s.c"`. It depends on the DCE/RPC server framework, talloc allocation conventions, and tevent for asynchronous sleep. It also includes `system/filesys.h` for `sleep()`.

## Risks and Edge Cases
- `SourceData()` fills a `uint8_t` array from an unsigned integer loop, so values wrap after 255 by design or by C conversion.
- `TestDoublePointer()` carefully checks the first two pointer levels before triple dereference; generated NDR pointer semantics are important here.
- `TestSleep()` trusts the requested seconds value; very large sleeps can tie up a synchronous worker or schedule long-lived async state.
- This endpoint allows connect binds and is intended for testing; exposing it in production-like configurations should be deliberate.

## Test Signals
Useful tests are mostly NDR/RPC conformance checks: zero-length and nonzero `EchoData`, allocation failure simulation, `SourceData` content, all `TestCall2` levels and invalid level, NULL and non-NULL surrounding structures, double-pointer NULL combinations, synchronous sleep behavior, async timer reply behavior, and bind accessibility.
