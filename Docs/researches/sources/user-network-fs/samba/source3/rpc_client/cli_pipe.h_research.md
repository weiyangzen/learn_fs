# sources/user-network-fs/samba/source3/rpc_client/cli_pipe.h research

## Purpose

`cli_pipe.h` publishes the source3 RPC pipe client API implemented mainly by `cli_pipe.c` and partly by `cli_pipe_schannel.c`. It is the public contract used by higher-level Samba client code to open DCE/RPC pipes over SMB named pipes, TCP, ncalrpc, or local named pipes, bind them anonymously or with credentials, alter authentication/presentation contexts, and create binding handles for generated NDR stubs.

## Important APIs, types, and functions

The header forward-uses `struct rpc_pipe_client`, `struct pipe_auth_data`, `struct cli_state`, `struct cli_credentials`, `struct netlogon_creds_cli_context`, and generated `struct ndr_interface_table`. It includes `rpc_client/rpc_client.h` for RPC client structures and `auth/credentials/credentials.h` for credential ownership.

The bind API is `rpc_pipe_bind_send()`, `rpc_pipe_bind_recv()`, and synchronous `rpc_pipe_bind()`. Open APIs include asynchronous `rpc_pipe_open_np_send/recv()`, local `rpc_pipe_open_ncalrpc()`, local named-pipe `rpc_pipe_open_local_np()`, anonymous `cli_rpc_pipe_open_noauth()` and `cli_rpc_pipe_open_noauth_transport()`, credentialed `cli_rpc_pipe_open_with_creds()`, and reopen `cli_rpc_pipe_reopen_np_noauth()`.

Utility APIs are `rpccli_set_timeout()`, `rpccli_is_connected()`, `rpccli_ncalrpc_bind_data()`, `rpccli_anon_bind_data()`, `rpccli_bh_create()`, and `cli_rpc_pipe_client_prepare_alter()`. Schannel APIs are `cli_rpc_pipe_client_auth_schannel()`, `cli_rpc_pipe_open_bind_schannel()`, `cli_rpc_pipe_open_schannel_with_creds()`, and `cli_rpc_pipe_open_schannel()`.

## Control flow and contracts

Callers typically open a pipe for a generated interface table, obtain or construct `pipe_auth_data`, then bind. Convenience open helpers combine transport open and bind. The async named-pipe open returns an unbound `rpc_pipe_client`; callers then choose anonymous or authenticated bind. `rpccli_bh_create()` is normally called during bind but is exposed for code that needs a binding handle tied to an existing pipe.

The comment on `cli_rpc_pipe_open_with_creds()` says the routine steals or references the passed credentials depending on historical wording, while the implementation passes credentials into `auth_generic_set_creds()` and then moves the GENSEC security context into `pipe_auth_data`. Callers should not assume this header is a standalone ownership specification; the implementation and talloc hierarchy are authoritative.

## State and persistence behavior

The API manages in-memory connection, binding, authentication, and credential state. No persistent storage is exposed here. Functions that take `TALLOC_CTX *mem_ctx` return talloc-owned objects under that context. Several bind-data constructors allocate `pipe_auth_data` whose `auth_context_id` is intentionally left as `UINT32_MAX` so `rpc_pipe_bind_send()` can allocate a unique context id.

## Dependencies and integration points

This header is a hub between source3 SMB client code, auth/gensec credentials, generated NDR interfaces, Netlogon schannel credential state, and the lower transport implementations. Service-specific wrappers such as `cli_samr.c`, `cli_spoolss.c`, and `cli_winreg.c` depend on `rpc_pipe_client->binding_handle` after these APIs complete.

## Risks and test signals

API misuse risks include binding with an auth object whose lifetime is not transferable, calling generated stubs before a successful bind, attempting `cli_rpc_pipe_client_prepare_alter()` without requesting either a new auth or presentation context, and using schannel helpers without valid Netlogon credentials. Tests should compile all callers against this header, exercise async open/recv ownership, verify timeout and connected-state behavior, and cover all convenience open paths advertised here.
