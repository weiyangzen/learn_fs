# sources/user-network-fs/samba/source3/lib/netapi/cm.c

## sources/user-network-fs/samba/source3/lib/netapi/cm.c

Purpose: Provides libnetapi connection management for IPC$ SMB sessions and cached DCERPC pipes.

Important APIs/types/functions: `client_ipc_connection` holds a server name, `cli_state`, and pipe list. `client_pipe_connection` wraps `rpc_pipe_client`. Exported functions are `libnetapi_shutdown_cm()`, `libnetapi_open_pipe()`, and `libnetapi_get_binding_handle()`. Internal helpers find/open IPC sessions and pipes.

Control flow: Opening a pipe first finds or creates an IPC connection for the server, collecting username/password, configuring credential callbacks and Kerberos state, and calling `cli_cm_open()`. Pipe lookup validates connection liveness and abstract syntax. Missing pipes are opened with `cli_rpc_pipe_open_noauth()` and cached under the IPC connection. Shutdown iterates cached IPC sessions and closes SMB connections.

State and persistence behavior: State lives under `libnetapi_ctx` as talloc-owned linked lists. No disk persistence. Cached connections preserve authenticated sessions and pipe handles for the context lifetime.

Dependencies and integration points: Integrates libnetapi APIs with Samba client SMB, credentials, RPC pipe, `smbXcli`, `ndr_table`, WERROR/NTSTATUS conversion, and error-string storage.

Risks: Cached pipes can go stale and are checked before reuse. Kerberos state is mutated when credentials are incomplete. Server-name matching relies on remote names from SMB connections.

Test signals: Integration tests need repeated calls against the same server/interface, credential prompting paths, Kerberos/no-password behavior, stale pipe recovery, and `libnetapi_shutdown_cm()` cleanup.
