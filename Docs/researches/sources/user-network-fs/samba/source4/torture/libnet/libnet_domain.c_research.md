# sources/user-network-fs/samba/source4/torture/libnet/libnet_domain.c

## Purpose
`libnet_domain.c` exercises libnet domain open, close, and list operations over both LSA and SAMR. It validates that high-level `libnet_DomainOpen`, `libnet_DomainClose`, and `libnet_DomainList` calls correctly establish RPC connections, cache handles in `libnet_context`, and handle paged enumeration.

## Important APIs, types, and functions
The local helpers `test_opendomain_samr()` and `test_opendomain_lsa()` manually open domain policy handles through generated DCERPC client stubs. Public torture entry points cover LSA open/close, SAMR open/close, and domain listing. Key structures include `libnet_context`, `libnet_DomainOpen`, `libnet_DomainClose`, `libnet_DomainList`, `policy_handle`, `lsa_String`, `samr_Connect`, `samr_LookupDomain`, `samr_OpenDomain`, and `lsa_OpenPolicy2`.

## Control flow
The open tests initialize a libnet context, attach command-line credentials, derive the workgroup from `lp_ctx`, call the libnet open API, then close the returned handle directly through LSA or SAMR RPC. The close tests perform a lower-level manual open first, populate the matching `ctx->lsa` or `ctx->samr` fields, and then ask `libnet_DomainClose` to close the preloaded state. The list test calls `libnet_DomainList` once with the default buffer and once with a deliberately small SAMR buffer to force multi-round enumeration.

## State and persistence behavior
No directory objects are created. Runtime state is the remote RPC connection, domain policy handles cached inside `libnet_context`, and temporary talloc allocations. Cleanup relies on closing remote handles and freeing the libnet context; failed intermediate paths can leave only server-side RPC context handles until connection teardown.

## Dependencies and integration points
The file integrates libnet with generated `ndr_samr_c` and `ndr_lsa_c` RPC clients, `torture_rpc_binding()`, command-line credentials, and Samba loadparm workgroup settings. It also depends on helpers declared in `torture/libnet/proto.h`.

## Risks and edge cases
Tests require a reachable DC and credentials with enough access to open domain policy handles. The close tests are sensitive to correct transfer of talloc-owned domain names and SIDs into `libnet_context`. The domain list path specifically probes paged enumeration and can expose resume-index or buffer-size regressions.

## Test signals
Success means LSA and SAMR domain handles can be opened and closed through both direct RPC and libnet wrappers, and domain enumeration works in one-shot and small-buffer modes. Failure messages include the exact NTSTATUS for connection, lookup, open, close, or list failures.
