# sources/user-network-fs/samba/source4/rpc_server/eventlog/dcesrv_eventlog6.c

## Purpose
`dcesrv_eventlog6.c` is a minimal server stub for the Windows EventLog6 RPC interface. Most operations are intentionally unimplemented and fault with `DCERPC_FAULT_OP_RNG_ERROR`. Two methods return success: `EvtRpcRegisterLogQuery`, which creates placeholder handles, and `EvtRpcQueryNext`, which returns `WERR_OK` without populating event data.

The file exists to expose enough of the generated interface for limited client compatibility or test coverage, not to provide a complete event log service.

## Important APIs, Types, and Functions
- `dcesrv_eventlog6_EvtRpcRegisterLogQuery()` creates two generic DCE/RPC handles via `dcesrv_handle_create()`: one query handle and one operation-control handle. It returns their wire handles.
- `dcesrv_eventlog6_EvtRpcQueryNext()` returns `WERR_OK` directly.
- All other static `dcesrv_eventlog6_*` methods call `DCESRV_FAULT(DCERPC_FAULT_OP_RNG_ERROR)`, including subscription, clear/export, render, seek, close, cancel, config, channel, publisher, metadata, and display-name operations.
- The generated server dispatch table is included through `librpc/gen_ndr/ndr_eventlog6_s.c`.

## Control Flow
Every RPC operation is a small static handler matching generated NDR prototypes. Most handlers immediately raise an operation-range fault. `EvtRpcRegisterLogQuery` allocates a server handle for `r->out.handle`, allocates a second server handle for `r->out.opControl`, and returns `WERR_OK` if both allocations succeed. `EvtRpcQueryNext` returns success without any visible validation, handle lookup, result count setup, or event buffer population in this source file.

## State and Persistence Behavior
There is no event log persistence and no backing query state. The only state created is generic DCE/RPC handle state from `dcesrv_handle_create()`, but no private data is attached to the handles. There is no explicit close implementation; `EvtRpcClose` faults rather than freeing handles.

## Dependencies and Integration Points
The file depends on the DCE/RPC server framework, generated EventLog6 NDR definitions, and common RPC server helpers. It integrates with generated dispatch by including `ndr_eventlog6_s.c`. It does not integrate with a log database, filesystem event log files, registry channel configuration, publisher metadata store, or access-control checks in this implementation.

## Risks and Edge Cases
- Returning success from `EvtRpcQueryNext` without event data may confuse clients that expect output fields to be meaningful. The generated marshalling layer may zero defaults, but semantic completeness is absent.
- `EvtRpcRegisterLogQuery` creates handles with type `0` and no private payload, so later operations cannot distinguish or validate query versus operation-control state in this file.
- `EvtRpcClose` and `EvtRpcCancel` fault, so clients cannot explicitly release or cancel the placeholder handles through this interface.
- Because most operations fault as operation-range errors, client compatibility depends on whether clients tolerate the stub behavior.
- There are no explicit access checks; the practical risk is limited by the lack of implemented data access, but any future implementation must add authorization around channel/query operations.

## Test Signals
Tests should verify that each unimplemented operation faults consistently, `EvtRpcRegisterLogQuery` returns two non-null handles on success and handles allocation failure, `EvtRpcQueryNext` returns `WERR_OK` with expected generated default outputs, and clients do not leak server handles indefinitely when close/cancel are unavailable. Compatibility tests with Windows eventlog clients should assert the exact observed behavior expected from this stub.
