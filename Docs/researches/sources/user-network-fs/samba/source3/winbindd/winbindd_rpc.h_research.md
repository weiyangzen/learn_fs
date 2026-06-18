<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_rpc.h -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_rpc.h

## Purpose
This header declares the low-level RPC helper interface implemented by `winbindd_rpc.c`. It is the contract between SAMR/LSA pipe management code and the reusable query/membership/trust routines.

## Important APIs, Types, And Functions
The declarations cover `rpc_query_user_list`, group enumeration, user group and alias lookup, group and alias member expansion, and trusted-domain enumeration. The API surface uses `TALLOC_CTX`, `rpc_pipe_client`, `policy_handle`, `dom_sid`, `wb_acct_info`, `netr_DomainTrust`, and NTSTATUS.

## Control Flow
The header has no runtime control flow. Its declarations imply callers must establish and pass valid SAMR or LSA pipe clients plus domain or policy handles before calling the helpers.

## State And Persistence Behavior
No state is defined here. Ownership is expressed by talloc output pointers: result arrays are allocated under the provided memory context and returned through out parameters.

## Dependencies And Integration Points
It is included by `winbindd_rpc.c` and `winbindd_samr.c`. The header depends on types declared by broader Samba winbind/RPC headers included before or alongside it.

## Risks And Test Signals
The main risk is API drift between this header and `winbindd_rpc.c` or callers. Compile coverage of winbindd with SAMR support is the primary signal, supplemented by tests that exercise every declared helper through `sam_passdb_methods`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_rpc.h -->
