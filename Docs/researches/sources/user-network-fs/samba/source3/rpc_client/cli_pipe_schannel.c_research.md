# sources/user-network-fs/samba/source3/rpc_client/cli_pipe_schannel.c research

## Purpose

`cli_pipe_schannel.c` provides the high-level "open a pipe using schannel if appropriate" helper. It obtains domain trust credentials, establishes or reuses Netlogon credential state, chooses between Kerberos privacy, schannel authenticated RPC, and anonymous RPC based on negotiated Netlogon capabilities, and returns an opened `rpc_pipe_client`.

## Important APIs, types, and functions

The sole exported function is `cli_rpc_pipe_open_schannel()`. It accepts an SMB `cli_state`, messaging context, target interface table, transport, domain, remote name and address, output pipe, and optional output Netlogon credentials context. It uses `pdb_get_trust_credentials()`, `cli_credentials_add_gensec_features()`, `rpccli_create_netlogon_creds_ctx()`, `rpccli_connect_netlogon()`, `rpccli_setup_netlogon_creds()`, `netlogon_creds_cli_get()`, `cli_rpc_pipe_open_with_creds()`, `cli_rpc_pipe_open_schannel_with_creds()`, and `cli_rpc_pipe_open_noauth()`.

## Control flow

The function first loads trust credentials for the requested domain and disables delegation on those credentials. It creates a Netlogon credential context for the remote host. If the requested table is the Netlogon interface itself, it calls `rpccli_connect_netlogon()` and returns that pipe.

For other interfaces it establishes Netlogon credentials with `rpccli_setup_netlogon_creds()`, fetches the negotiated credential state, and inspects `negotiate_flags` and `authenticate_kerberos`. If Kerberos authentication was negotiated, it opens the target pipe with `DCERPC_AUTH_TYPE_KRB5` and privacy level using target service `"netlogon"`. If the server supports `NETLOGON_NEG_AUTHENTICATED_RPC`, it opens with schannel credentials. Otherwise it falls back to an anonymous named-pipe open.

## State and persistence behavior

State is talloc-scoped to a temporary frame until success. On success, the `rpc_pipe_client` is returned through `presult`; if `pcreds` is non-NULL, the Netlogon credentials context is moved to the caller's `mem_ctx`. Trust credentials and Netlogon credential state may internally come from passdb or credential caches, but this function itself writes no persistent data.

## Dependencies and integration points

The file integrates passdb trust account credential retrieval, GENSEC features, source3 Netlogon RPC helpers, Netlogon credential cache/locking code, and the generic pipe open/bind functions from `cli_pipe.c`. It is used by code that wants a secure RPC pipe without manually handling Netlogon negotiation details.

## Risks and test signals

The key risk is selecting the wrong authentication mode after Netlogon setup. Kerberos mode forces privacy and service `"netlogon"`; schannel mode requires valid machine account credentials; the fallback anonymous path may be insecure but preserves compatibility with servers lacking authenticated RPC flags. Tests should cover Netlogon table short-circuit, Kerberos-authenticated credential state, schannel-authenticated state, no-auth fallback, trust credential lookup failure, and propagation of a returned `netlogon_creds_cli_context`.
