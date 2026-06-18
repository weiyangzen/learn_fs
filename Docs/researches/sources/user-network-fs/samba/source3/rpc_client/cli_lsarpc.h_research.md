<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_lsarpc.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_lsarpc.h

Purpose: Public header for Samba LSA RPC client convenience routines.

Important APIs, types, and functions: Declares LSA policy-open helpers, SID-to-name lookup helpers, name-to-SID lookup helpers, generic variants that select lookup level and newer RPC opnums, and `fetch_domain_sid()`.

Control flow: No executable logic. The prototypes expose both `dcerpc_binding_handle` APIs that return transport status plus an out `result`, and `rpc_pipe_client` wrappers that collapse the RPC result into the function return after transport success.

State and persistence behavior: No header-owned state. Output arrays and policy handles are allocated or filled by implementations using caller memory contexts.

Dependencies and integration points: Included by callers that need account/domain translation over LSARPC. It depends on generated LSA types, `policy_handle`, `dom_sid`, and `rpc_pipe_client` declarations from surrounding Samba headers.

Risks: Some prototypes use `int` for counts while others use `uint32_t`; callers must avoid negative values reaching unsigned RPC fields. The `fetch_domain_sid()` declaration is not implemented in the paired source file, indicating it is provided elsewhere or stale.

Test signals: Compile coverage for callers, API compatibility checks for generated LSA type changes, and behavior tests in `cli_lsarpc.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_lsarpc.h -->
