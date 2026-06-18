# sources/user-network-fs/samba/source4/rpc_server/epmapper/rpc_epmapper.c

## Purpose
`rpc_epmapper.c` implements the server side of the endpoint mapper pipe. It enumerates registered RPC interfaces and maps abstract interface towers to concrete endpoint towers for clients trying to discover where and how to bind to services.

Only lookup, map, and lookup-handle-free are implemented. Insert, delete, inquiry, management delete, and authenticated map operations fault with `DCERPC_FAULT_OP_RNG_ERROR`.

## Important APIs, Types, and Functions
- `dcesrv_interface_epmapper_bind()` allows clients to bind to the endpoint mapper.
- `struct dcesrv_ep_iface` pairs an interface name with an `epm_tower`.
- `build_ep_list()` walks `dce_call->conn->dce_ctx->endpoint_list`, duplicates each endpoint binding, sets the abstract syntax to each registered interface syntax id, builds a tower, and returns a talloc array of available endpoint/interface pairs.
- `dcesrv_epm_Lookup()` pages through the built endpoint list using a DCE/RPC context handle of type `HTYPE_LOOKUP`.
- `dcesrv_epm_Map()` parses a client-supplied tower, validates transfer syntax, determines transport, searches available towers for matching transport and abstract syntax, and returns the concrete tower.
- `dcesrv_epm_LookupHandleFree()` frees a lookup context handle and zeros the output handle.

## Control Flow
`Lookup` pulls or creates an `HTYPE_LOOKUP` handle. On the first call, it allocates a small `rpc_eps` state object on the handle and fills it with all registered endpoints from `build_ep_list()`. It returns at most `max_ents` entries, each with a zero object UUID, interface annotation, and tower pointer. It then advances the internal array pointer and decrements the count. When no entries remain, it returns `EPMAPPER_STATUS_NO_MORE_ENTRIES`, zeros the wire handle, and frees the server handle.

`Map` builds a fresh endpoint list for the call, prepares default output containers, and rejects missing towers, zero `max_towers`, or towers with fewer than three floors. It extracts the abstract syntax from floor 0 and transfer syntax from floor 1, requires NDR transfer syntax, and derives the transport from the tower. It then scans available endpoint towers for matching transport and abstract syntax. On success it returns one tower; on failure it sets `num_towers` to zero and clears the tower pointer.

## State and Persistence Behavior
There is no durable persistence. Lookup state is stored in a DCE/RPC handle between paged `Lookup` calls. `build_ep_list()` snapshots the current endpoint list into talloc memory for that handle or call. `Lookup` mutates the saved pointer by advancing it, so the original base pointer is no longer directly retained after paging.

## Dependencies and Integration Points
The file depends on generated epmapper NDR types, DCE/RPC binding/tower helpers, endpoint registration data in `dcesrv_context`, and DCE/RPC handle macros. It is an integration point for every registered RPC endpoint because discovery output comes from `dce_ctx->endpoint_list`.

## Risks and Edge Cases
- `build_ep_list()` returns zero on allocation failures and also skips tower-build failures after logging. Callers see an empty or partial endpoint list rather than a detailed error.
- `Lookup` advances `eps->e` after each page; this is simple but means the saved pointer no longer points to the allocation base. Talloc ownership still comes from the handle allocation, but future changes must not free the advanced pointer directly.
- `Map` allocates output tower containers before validating input and returns `NO_MORE_ENTRIES` for many malformed inputs rather than a more specific fault.
- Only NDR transfer syntax is supported. Requests using unsupported transfer syntax or unknown transport are silently mapped to no entries.
- Unsupported management methods fault, so clients expecting dynamic registration APIs will not work.

## Test Signals
Tests should cover endpoint enumeration over multiple `Lookup` pages, handle exhaustion and handle-free behavior, empty endpoint lists, malformed towers, non-NDR transfer syntax, unknown transport floors, successful map by abstract syntax and transport, transport mismatch, abstract syntax mismatch, and unsupported operations faulting with operation-range errors.
