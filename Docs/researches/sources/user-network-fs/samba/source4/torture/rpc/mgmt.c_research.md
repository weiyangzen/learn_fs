# sources/user-network-fs/samba/source4/torture/rpc/mgmt.c

## Purpose

This file tests the DCE/RPC management interface (`mgmt`) across all registered/mappable Samba RPC interfaces. It verifies that management endpoints report interface IDs, statistics, principal names, server-listening state, and refusal to honor stop-listening requests.

## Important APIs, Types, and Functions

The file uses generated `ndr_mgmt_c.h` stubs and the NDR interface registry. `test_inq_if_ids()` is exported and reusable: it calls `mgmt_inq_if_ids`, logs each returned syntax UUID/version/name, and optionally invokes a caller-provided callback for each ID. Local helpers include `test_inq_stats()`, `test_inq_princ_name_size()`, `test_inq_princ_name()`, `test_is_server_listening()`, `test_stop_server_listening()`, and `torture_rpc_mgmt()`.

The principal-name tests integrate with GENSEC by mapping auth types to names through `gensec_get_name_by_authtype()`. `torture_rpc_mgmt()` uses `ndr_table_list()`, endpoint mapper binding via `dcerpc_epm_map_binding()`, and `lpcfg_set_cmdline()` to retarget the torture binding per interface.

## Control Flow

`torture_rpc_mgmt()` obtains a base binding, iterates over every registered NDR interface, skips unmappable tables and the management interface itself, maps a concrete endpoint for the current interface, updates `torture:binding`, and connects to the mgmt interface at that endpoint. Missing interfaces are skipped; unexpected connection errors mark the overall result false.

For each reachable endpoint it runs `is_server_listening`, `stop_server_listening`, `inq_stats`, `inq_princ_name`, and `inq_if_ids`. `test_inq_princ_name()` probes auth protocol numbers 0 through 255, records any successful principal names, and for Kerberos, NTLMSSP, and SPNEGO calls `test_inq_princ_name_size()` to verify buffer sizing behavior: size 0 should produce bad stub data, undersized buffers should return `WERR_INSUFFICIENT_BUFFER`, and `len + 1` should succeed.

## State and Persistence Behavior

The test changes only client-side binding configuration during iteration. It must not stop servers; `test_stop_server_listening()` treats a successful stop request as a failure because the endpoint should refuse it. Memory is scoped with talloc contexts, although the loop context is freed only on some paths in the current code shape.

## Dependencies and Integration Points

Dependencies include the endpoint mapper, generated mgmt client stubs, NDR table registry, GENSEC auth-type names, Samba loadparm context, and the common RPC torture connection helpers. The test dynamically covers every interface registered in the process, so adding or removing NDR tables changes the set of endpoints that are probed.

## Risks and Edge Cases

The suite is environment-dependent because not every registered interface is necessarily available on the target server or transport. Endpoint mapping failures are logged and skipped, while connection failures other than `NT_STATUS_OBJECT_NAME_NOT_FOUND` mark failure. Principal-name behavior varies by authentication provider; the code deliberately only enforces exact buffer-size behavior for KRB5, NTLMSSP, and SPNEGO. A server that actually honors `mgmt_stop_server_listening` would create a severe behavioral and test failure.

## Test Signals

Signals include successful `mgmt_inq_if_ids` with a non-NULL vector, stats array count equal to `MGMT_STATS_ARRAY_MAX_SIZE`, expected principal-name buffer errors and success thresholds, listening-state RPC success, refusal of `stop_server_listening`, and successful per-interface endpoint traversal. Output comments include UUID/version/interface names and management counters, which are useful diagnostics when a specific RPC endpoint changes availability.
