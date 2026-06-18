# sources/object-store/daos/src/engine/rpc.c

## Purpose
`rpc.c` contains server RPC utility wrappers around CART calls. It offers a synchronous send helper for ULT context and a reply helper that honors DAOS fail-location injection.

## Important APIs, Types, and Functions
`dss_rpc_send(crt_rpc_t *rpc)` sends a CART RPC and waits for completion through an Argobots eventual. `dss_rpc_reply(crt_rpc_t *rpc, unsigned int fail_loc)` sends a reply unless the supplied fail location is active. The private callback `rpc_cb` copies `cci_rc` into the eventual.

## Control Flow
`dss_rpc_send` creates an `ABT_eventual`, adds a CART request reference, sends the RPC with `crt_req_send`, waits for the callback to set completion status, frees the eventual, and returns the callback status. `dss_rpc_reply` checks `DAOS_FAIL_CHECK`; when not dropping the reply it calls `crt_reply_send` and logs failures.

## State and Persistence Behavior
No persistent state is owned here. The send helper temporarily owns an eventual and adds a CART request reference, relying on CART request lifecycle rules for the extra reference. The result status is transferred through callback memory owned by Argobots eventual storage.

## Dependencies and Integration Points
The file depends on `daos_srv/daos_engine.h` for CART, Argobots, DAOS error conversion, logging, and fail injection. It is a utility for server modules that need blocking-style RPC send/reply semantics inside ULTs.

## Risks
Blocking on `ABT_eventual_wait` requires the associated CART context to keep progressing elsewhere; otherwise deadlock is possible. If `crt_req_send` fails, the function frees the eventual but relies on request reference handling outside this wrapper. The reply helper silently drops replies when fail injection is enabled, which is intentional but can obscure tests if fail locations leak between cases.

## Test Signals
Useful tests include successful send completion, send callback error propagation, Argobots eventual create/wait failures, reply send failure logging, fail-location reply drop behavior, and integration tests proving the relevant CART context progresses while synchronous waits are active.
