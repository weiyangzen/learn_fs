# sources/user-network-fs/samba/source3/winbindd/winbindd_dual_ndr.c

## Purpose
Implements the internal parent-to-child wbint transport using Samba's NDR/DCERPC infrastructure without full network DCERPC fragmentation. It lets parent code call generated `dcerpc_wbint_*` stubs while actually sending a compact `WINBINDD_DUAL_NDRCMD` request over the winbind child socket.

## Important APIs, Types, And Control Flow
`wbint_binding_handle()` builds a `dcerpc_binding_handle` with custom `wbint_bh_ops`. `wbint_bh_raw_call_send()` checks connection state, serves cache hits with `wcache_fetch_ndr()`, wraps opnum and marshalled input in `struct winbindd_request`, and dispatches either to `wb_child_request_send()` for special children or `wb_domain_request_send()` for domain children. Completion callbacks copy response extra data into `out_data`; domain calls also store successful replies with `wcache_store_ndr()`. `winbindd_dual_ndrcmd()` runs in a child: it creates an internal NCACN connection and dcesrv connection, sets socket-derived local/remote addresses, dispatches the generated server call via `dcesrv_call_dispatch_local()`, and moves the reply blob into `state->response`.

## State And Persistence
Binding state holds either a domain or child pointer plus the synthetic binding. Domain calls may persist NDR responses in winbind cache. Child-side dispatch uses stackframe/talloc lifetime and does not itself write files.

## Dependencies And Integration Points
Depends on generated `ndr_winbind`, DCERPC server core, RPC server config, `wb_domain_request`, `wb_child_request`, winbind cache NDR helpers, tsocket address conversion, and global dcesrv context callbacks.

## Risks And Test Signals
`set_timeout()` is a stub, so higher-level timeout expectations may not apply. Opnum bounds rely on generated table callers. Risks include cache coherency for NDR replies, invalid response lengths, stale domain refs, and local dcesrv endpoint discovery failure. Test cache hit/miss behavior, idmap/locator/domain binding paths, child socket peer address failures, generated wbint call round-trips, and malformed/oversized NDR payloads.
