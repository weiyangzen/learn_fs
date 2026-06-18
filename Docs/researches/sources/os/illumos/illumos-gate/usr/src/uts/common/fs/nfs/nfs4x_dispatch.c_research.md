# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_dispatch.c

## Purpose

`nfs4x_dispatch.c` is the NFSv4.1 server dispatch wrapper for COMPOUND RPCs. It validates session-oriented compound layout, prepares NFSv4.1 sequence/replay-cache state, calls the common NFSv4 compound executor, and coordinates reply encoding with slot cleanup.

## Main Interfaces

Main functions:

- `rfs4x_dispatch(struct svc_req *req, SVCXPRT *xprt, char *ap)`

Private helpers:

- `rfs4_err_resp()`
- `valid_first_compound_op()`
- `verify_compound_args()`
- `rfs4x_dispatch_done()`
- `xdr_compound_wrapper()`

## Behavior

`verify_compound_args()` enforces the NFSv4.1 session rules for compounds:

- Empty compounds are accepted.
- The first operation must be `OP_BIND_CONN_TO_SESSION`, `OP_SEQUENCE`, `OP_EXCHANGE_ID`, `OP_CREATE_SESSION`, `OP_DESTROY_SESSION`, `OP_DESTROY_CLIENTID`, or `OP_ILLEGAL`.
- If the first operation is not `OP_SEQUENCE`, the request is outside a session and must contain exactly one operation.

`rfs4x_dispatch()` initializes `compound_state_t`, verifies the request, and calls `rfs4x_sequence_prep()`. If sequence preparation reports a replay-cache hit, dispatch skips normal compound execution and sends the cached response. Otherwise it runs `rfs4_compound()` with `T_DONTPEND` set to avoid RPC pending behavior during server compound execution.

## Reply And Cleanup Flow

Replies are sent through `svc_sendreply()` using `xdr_compound_wrapper()`. The wrapper only calls `rfs4x_dispatch_done()` when XDR is encoding real reply data, which matters because some XDR sizing/probing paths should not mutate slot state.

`rfs4x_dispatch_done()` either:

- Calls `rfs4x_sequence_done()` when the compound owns an NFSv4.1 slot, allowing the slot reply cache to be updated and the slot released.
- Frees the compound response directly for non-session compounds.

`RFS4_DISPATCH_DONE` prevents double cleanup if sendreply fails or if the wrapper already completed cleanup.

## Dependencies

This file depends on common NFSv4 server execution (`rfs4_compound`, `rfs4_compound_free`, compound-state init/fini) and NFSv4.1 session helpers in `nfs4x_srv.c`.

## Research Notes

The important invariant is that slot release and response freeing happen after real reply encoding, not merely after response construction. The dispatch code is small, but it is the handoff point between RPC transport behavior and the NFSv4.1 session replay cache.
