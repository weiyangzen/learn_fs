<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_netlogon.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_netlogon.h

Purpose: Public header for NETLOGON RPC client credential setup, pipe connection, and SAM logon helpers.

Important APIs, types, and functions: Forward declares required Samba client, messaging, credential, netlogon credential, and binding-handle types. Declares `rpccli_pre_open_netlogon_creds()`, `rpccli_create_netlogon_creds_ctx()`, `rpccli_setup_netlogon_creds()`, `rpccli_connect_netlogon()`, and three logon helpers for password, network, and interactive logon modes.

Control flow: No executable logic. The APIs separate credential-cache setup, authenticated netlogon pipe creation, and individual logon request construction.

State and persistence behavior: No header-owned state. Implementations persist credential state through the netlogon creds cache and return validation info allocated on caller talloc contexts.

Dependencies and integration points: Included by winbind, domain join/trust, and authentication client code needing secure Netlogon operations. It includes common RPC transport definitions and uses generated Netlogon enum/union types.

Risks: The signatures expose raw password, hash, challenge, and response blobs; callers must manage secret lifetimes and pass correct logon info classes. Output validation pointers must be checked only after `NT_STATUS_OK`.

Test signals: Compile coverage for Netlogon consumers and behavioral tests in `cli_netlogon.c`, especially parameter validation and ownership of returned validation unions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_netlogon.h -->
