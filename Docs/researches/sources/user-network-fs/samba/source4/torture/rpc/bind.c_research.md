# sources/user-network-fs/samba/source4/torture/rpc/bind.c

## Purpose
`bind.c` is the DCE/RPC bind torture suite. It verifies authenticated LSARPC binds with NTLM/SPNEGO, signing, sealing, optional big-endian NDR, and endpoint mapper association-group handle sharing across TCP connections.

## Important APIs, types, and functions
The suite entry point is `torture_rpc_bind()`. Helpers are `test_openpolicy()`, `test_bind()`, `test_assoc_group_handles_external()`, and `test_bind_op()`. It uses `dcerpc_binding_set_flags()`, `dcerpc_pipe_connect_b()`, `dcerpc_binding_set_transport()`, `dcerpc_binding_set_string_option()`, `dcerpc_binding_get_assoc_group_id()`, `dcerpc_binding_set_assoc_group_id()`, LSARPC policy helpers, and EPM calls `dcerpc_epm_Lookup_r()` and `dcerpc_epm_LookupHandleFree_r()`.

## Control flow
For each authentication flag combination, `test_bind()` parses the configured binding, applies auth/sign/seal flags, connects to LSARPC with command-line credentials, opens and closes an LSA policy handle, then frees the pipe. The suite registers NTLM sign, NTLM sign/seal, SPNEGO sign, SPNEGO sign/seal, and big-endian variants of each. The association-group test opens an endpoint mapper TCP pipe on port 135, starts an EPM lookup to obtain a context handle, opens a second pipe in a different association group and expects `RPC_SS_CONTEXT_MISMATCH` when using that handle, then reconnects the second pipe with the first pipe's association group ID and expects the handle to work. It finally frees the EPM lookup handle.

## State and persistence behavior
State is RPC association/binding state and transient LSA/EPM context handles. No server data is persisted. The association-group test deliberately carries an EPM context handle across connections only when the same association group is requested.

## Dependencies and integration points
The file depends on generated LSARPC and EPMAPPER stubs, command-line credentials, DCE/RPC binding parsing, TCP endpoint 135, auth option flags, and torture helper policy functions. It validates client and server support for authentication flavors, sealing, byte order, and association group semantics.

## Risks and edge cases
Big-endian push support can expose NDR marshalling assumptions. Association group behavior is interface/process dependent; the comment avoids LSARPC for handle sharing because preforked selftests can put interfaces in different processes. The cleanup assertion after `LookupHandleFree` checks `r.out.result` instead of `f.out.result`, which may miss a cleanup failure. Port 135 may be unavailable for non-TCP bindings or restricted environments.

## Test signals
Signals are successful bind and LSA open/close for every auth/sign/seal/endian combination, context mismatch for a handle used in a different association group, success after reusing the original association group ID, and successful EPM handle cleanup.
