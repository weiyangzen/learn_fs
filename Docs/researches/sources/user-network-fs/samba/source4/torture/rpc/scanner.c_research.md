# sources/user-network-fs/samba/source4/torture/rpc/scanner.c

## Purpose

This file implements `torture_rpc_scanner()`, a generic RPC endpoint scanner for Samba torture. It iterates every locally registered NDR interface, maps or binds to the interface on the target server, asks the RPC management interface for advertised interface IDs, and probes procedure numbers with raw calls to estimate how many calls are available.

## Important APIs, Types, and Functions

- `test_num_calls()` is the callback used by management interface enumeration. It connects to an interface syntax ID, sends synthetic raw calls with a 1000-byte `0xFF` stub body, and stops on out-of-range, access-denied, protocol-error, disconnect, or 200 calls.
- `torture_rpc_scanner()` retrieves the base binding, loops through `ndr_table_list()`, maps endpoints over TCP with `dcerpc_epm_map_binding()` or sets named-pipe endpoint/abstract syntax directly, connects to the `mgmt` interface, and calls `test_inq_if_ids()`.
- `ndr_table_by_syntax()` is used to match advertised syntaxes back to local IDL metadata; unknown syntaxes are represented by a synthetic table with `UINT32_MAX` calls.

## Control Flow

The scanner obtains the torture binding and determines transport. It skips local tables with zero calls and the management interface itself. For each remaining local interface it prints the pipe name, maps or rewrites the binding for that interface, stores the binding string back into `torture:binding`, connects to `ndr_table_mgmt`, and calls `test_inq_if_ids()`.

For each syntax ID returned by management, `test_num_calls()` opens a pipe to that syntax. If the interface is unknown locally, it constructs a temporary table using the original interface as a template but with the advertised syntax ID. It then repeatedly calls `dcerpc_binding_handle_raw_call()` for opnums 0 through 199. `NT_STATUS_RPC_PROCNUM_OUT_OF_RANGE` ends the count. Access denied and disconnect stop early. Protocol errors are reported but scanning continues. The final count is compared with local IDL `num_calls` when known.

## State and Persistence Behavior

The scanner does not mutate server state intentionally, but raw calls with invalid stubs may still reach server-side dispatch paths. Local state is limited to temporary talloc loop contexts, binding-string updates inside the torture loadparm context, and printed diagnostic output.

## Dependencies and Integration Points

It depends on generated management RPC bindings, the global NDR interface registry, endpoint mapper support, raw DCERPC call support, and `test_inq_if_ids()` from the management torture helpers. It is transport-aware and handles `NCACN_IP_TCP` differently from named-pipe style transports.

## Risks and Edge Cases

The probe sends malformed input to every discovered opnum, so it can trigger server bugs, noisy logs, or disconnects. A hard 200-call limit may undercount very large interfaces. Access-denied results stop a scan even if later opnums would be visible. The scanner mutates the shared `torture:binding` setting while iterating, which can surprise code that assumes it remains the original binding.

## Test Signals

The main signal is diagnostic rather than strict assertion: for each interface, it reports the discovered call count and whether it matches local IDL. The function returns false on binding/setup failures or failed management enumeration, but many per-interface connection failures are printed and treated as non-fatal so the scanner can continue.
