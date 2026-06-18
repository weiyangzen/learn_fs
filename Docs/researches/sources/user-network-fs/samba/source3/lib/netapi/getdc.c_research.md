# sources/user-network-fs/samba/source3/lib/netapi/getdc.c

## Purpose

`getdc.c` implements libnetapi domain-controller discovery calls. It was read as a complete 212-line file. The module covers legacy NetLogon DC-name APIs (`NetGetDCName`, `NetGetAnyDCName`) and `DsGetDcName`, using either remote NETLOGON RPC or Samba's local `dsgetdcname()` locator.

## Important APIs, Types, and Functions

The main functions are `NetGetDCName_r/_l`, `NetGetAnyDCName_r/_l`, and `DsGetDcName_r/_l`. Remote legacy calls bind to `ndr_table_netlogon` and call `dcerpc_netr_GetDcName` or `dcerpc_netr_GetAnyDCName`. `DsGetDcName_l` uses `struct libnetapi_private_ctx`, `priv->msg_ctx`, and `dsgetdcname`; `DsGetDcName_r` tries `dcerpc_netr_DsRGetDCNameEx` with a site name and falls back to `dcerpc_netr_DsRGetDCName`.

## Control Flow

Legacy local functions redirect to localhost. Legacy remote functions bind to NETLOGON, call the relevant RPC, allocate an API buffer sized by `strlen_m_term(dcname)`, copy the returned DC name, and store it in `r->out.buffer`. `DsGetDcName_l` directly performs local discovery and stores the returned `netr_DsRGetDCNameInfo` through the output pointer. `DsGetDcName_r` first requests the extended RPC variant and, if status or `werr` is not successful, retries the older call without `site_name`.

## State and Persistence Behavior

The file maintains no durable state. It allocates returned DC-name buffers through `NetApiBufferAllocate` for legacy calls and uses `ctx` for `DsGetDcName` results. Discovery may consult Samba locator caches or messaging state through `dsgetdcname`, but this module does not own that persistence.

## Dependencies and Integration Points

Dependencies include generated NETLOGON NDR, `libnetapi` generated structs, private binding helpers, `libsmb/dsgetdcname.h`, and the context private message state initialized in `netapi.c`. Public entry points are declared in `libnetapi.h` and wrapped by `libnetapi.c`.

## Risks and Edge Cases

The legacy remote functions assume a non-null `dcname` on successful RPC and allocate exact string length including terminator. `DsGetDcName_r` falls back broadly after any unsuccessful extended call, which improves compatibility but can hide site-specific failure causes. Error strings are set only on the local `DsGetDcName_l` path.

## Test Signals

Test with reachable and unreachable domains, explicit server names, null optional domain/site arguments, site-specific DC lookup, fallback to non-Ex RPC against older servers, and buffer-freeing via `NetApiBufferFree`.
