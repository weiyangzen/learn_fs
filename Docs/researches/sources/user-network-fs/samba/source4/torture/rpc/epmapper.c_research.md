# sources/user-network-fs/samba/source4/torture/rpc/epmapper.c

## Purpose
This file defines the `rpc.epmapper` smbtorture suite for exercising the DCE/RPC endpoint mapper interface. It validates endpoint lookup iteration, tower mapping, temporary endpoint insertion/deletion, and explicit lookup-handle cleanup through generated `dcerpc_epm_*` client stubs.

## Important APIs, Types, And Functions
The test case is registered by `torture_rpc_epmapper()`, which binds to `ndr_table_epmapper` and adds `Map_simple`, `Map_full`, `Lookup_simple`, `Lookup_terminate_search`, and `Insert_noreplace`. `display_tower()` formats `struct epm_tower` floors through `epm_floor_string()`. `test_Insert()` and `test_Delete()` build an endpoint tower from a `struct dcerpc_binding` with `dcerpc_binding_build_tower()` and call `dcerpc_epm_Insert_r()` or `dcerpc_epm_Delete_r()`. `test_Map_tcpip()` constructs a TCP endpoint-map request and validates the returned floors. `test_Lookup_simple()` and `test_Lookup_terminate_search()` drive `epm_Lookup` pagination and `epm_LookupHandleFree`.

## Control Flow
The suite creates an endpoint-mapper RPC tcase and runs independent tests against the same RPC interface. Lookup tests initialize an empty `policy_handle`, request all endpoint entries in batches, print returned annotations and towers, then assert the search ends with no more entries and an empty handle. The termination test stops after one batch and frees the non-empty lookup handle. The full mapping test inserts a synthetic TCP endpoint for a known object syntax, maps it back, then deletes it.

## State And Persistence Behavior
Most tests are read-only. `test_Insert()`, `test_Delete()`, `test_Map_full()`, and `test_Insert_noreplace()` mutate the endpoint mapper database by registering temporary endpoints. Insert tests are skipped when the `samba4` torture option is set, reflecting server compatibility and state-safety concerns. Cleanup depends on the delete call succeeding after insertion; failures between insert and delete can leave temporary `SMBTORTURE` or `smbtorture endpoint` entries.

## Dependencies And Integration Points
The file depends on generated endpoint mapper NDR stubs, NDR syntax tables, DCE/RPC binding helpers, endpoint tower conversion helpers, `is_ipaddress()`, and the Samba torture RPC harness. It integrates with endpoint mapper transport data through `struct epm_twr_t`, `struct epm_entry_t`, `struct epm_Map`, `struct epm_Lookup`, and `struct policy_handle`.

## Risks And Edge Cases
The inserted TCP binding uses a hard-coded IP and port only as tower data, so the test assumes the mapper accepts synthetic endpoints and later maps by interface syntax. Protocol-floor mutation in `test_Map_display()` reuses a tower from lookup results and changes floors in-place for TCP, HTTP, UDP, SMB, and NetBIOS probes, which can make debugging hard if later checks reuse the same entry. The lookup loops rely on correct empty-handle behavior to avoid leaked server-side search state.

## Test Signals
Strong signals are exact `EPMAPPER_STATUS_OK`, `EPMAPPER_STATUS_NO_MORE_ENTRIES`, `NT_STATUS_RPC_SS_CONTEXT_MISMATCH` absence, valid dynamic TCP ports, valid IP address strings, NDR transfer syntax matches, and empty lookup handles after natural completion. Insert/delete success and no-replace behavior are the mutation signals.
