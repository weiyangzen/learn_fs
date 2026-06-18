# Research: sources/user-network-fs/samba/source3/lib/netapi/netlogon.c

Purpose: implements `I_NetLogonControl` and `I_NetLogonControl2` over the NETLOGON DCE/RPC interface. It converts LANMAN-style control inputs and NETLOGON query outputs into the public `NETLOGON_INFO_*` buffers declared in `netapi.h`.

Important APIs/functions: `construct_data` maps a `NETLOGON_CONTROL_*` function code plus caller `data` bytes into `union netr_CONTROL_DATA_INFORMATION`. `construct_buffer` maps `union netr_CONTROL_QUERY_INFORMATION` levels 1 through 4 into `NETLOGON_INFO_1` through `NETLOGON_INFO_4`. `I_NetLogonControl_r` calls `dcerpc_netr_LogonControl`; `I_NetLogonControl2_r` calls `dcerpc_netr_LogonControl2` or `dcerpc_netr_LogonControl2Ex`; `_l` forms redirect to localhost.

Control flow: `I_NetLogonControl_r` obtains a NETLOGON binding, performs the RPC with the requested function/query level, converts NTSTATUS to WERROR on transport failure, honors returned WERROR, then builds the output buffer. `I_NetLogonControl2_r` first validates/builds control data, obtains the binding, selects the Ex RPC for `TC_VERIFY`, `SET_DBFLAG`, and `FORCE_DNS_REG`, then converts the query union into a caller-visible buffer.

State and persistence: no local persistent state is kept. Remote Netlogon controls can affect remote service behavior, trust rediscovery, debug flags, DNS registration, or trust validation depending on function code. Output buffers are talloc allocations under `ctx`.

Dependencies/integration: depends on generated NETLOGON client stubs, generated libnetapi request structs, public/private NetAPI headers, and binding acquisition through `libnetapi_get_binding_handle`. It is invoked by public wrappers generated around `I_NetLogonControl` and `I_NetLogonControl2`.

Risks: `construct_data` casts raw `uint8_t *` data directly to strings or uses `atoi`, so callers must supply NUL-terminated data for string/debug-level controls. Unsupported function codes return `WERR_INVALID_PARAMETER`; unsupported levels return `WERR_INVALID_LEVEL`. `construct_buffer` assumes the RPC returned the expected union arm for the requested level; malformed or unexpected server responses could expose null dereferences if generated stubs do not enforce that invariant.

Test signals: tests should cover levels 1-4, invalid levels, unsupported function codes, `LogonControl2Ex`-selected function codes, NULL data where domain/user data is required, and local redirect behavior. Integration tests require a domain controller or Samba Netlogon service.
