# sources/user-network-fs/samba/source3/winbindd/winbindd_cm.c

## Purpose

`winbindd_cm.c` is winbindd's domain-controller connection manager. It centralizes domain online/offline transitions, DC discovery, server affinity, SMB session setup, RPC pipe creation, schannel/Kerberos/NTLMSSP authentication selection, connection invalidation, and network-change messaging.

## Important APIs, Types, and Functions

- `struct dc_name_ip` pairs DC names with socket addresses.
- Online/offline flow: `set_domain_offline()`, private `set_domain_online()`, `set_domain_online_request()`, `winbind_msg_domain_offline()`, `winbind_msg_domain_online()`.
- DC and failure caches: `winbind_add_failed_connection_entry()`, `winbind_idmap_add_failed_connection_entry()`, `connect_preferred_dc()`, `find_dc()`, `fetch_current_dc_from_gencache()`.
- Credential helpers: `cm_get_ipc_userpass()`, `cm_get_ipc_credentials()`, `cm_is_ipc_credentials()`, `winbindd_get_trust_credentials()`.
- Connection lifecycle: `cm_prepare_connection()`, `cm_open_connection()`, `invalidate_cm_connection()`, `close_conns_after_fork()`, `init_dc_connection()`, `init_dc_connection_rpc()`.
- Domain metadata: `set_dc_type_and_flags_trustinfo()`, `set_dc_type_and_flags_connect()`, `set_dc_type_and_flags()`.
- Pipe APIs: `cm_connect_sam()`, `cm_connect_lsa()`, `cm_connect_lsat()`, `cm_connect_netlogon()`, `cm_connect_netlogon_secure()`, `wb_open_internal_pipe()`.
- Message handlers: `winbind_msg_ip_dropped()` and `winbind_msg_disconnect_dc()`.

## Control Flow

`init_dc_connection()` checks internal/BUILTIN special cases, verifies existing connection state, invalidates stale state, optionally learns trust metadata, and calls `cm_open_connection()`. `cm_open_connection()` tries up to three DC attempts via `find_dc()` and `cm_prepare_connection()`. DC discovery first uses forced DC/server affinity, skips negative connection cache entries, then falls back to AD DNS, site-aware lookup, NetBIOS, or DNS. Successful setup moves the domain online, clears global offline state, stores current DC info in gencache, updates KDC locator state, and chooses pipe auth level.

RPC pipe functions reuse `domain->conn`. SAMR and LSA prefer authenticated SPNEGO pipes, fall back to schannel/Kerberos, and only use anonymous when sealed-pipe and strong-key requirements permit. LSAT and NETLOGON prefer TCP for AD domains when available and fall back to named pipes when appropriate. Expired SMB2 sessions trigger limited invalidation-and-retry paths.

## State and Persistence Behavior

Most live state is in `struct winbindd_domain`: online/startup/initialized flags, backend, DC name/address, AD/trust flags, secure channel type, TCP capability, and `domain->conn` handles. Cross-process or persistent state is stored via server affinity cache, negative connection cache, gencache `CURRENT_DCNAME/<domain>`, KDC locator state, Samba messaging, and global offline state in the winbind cache. `invalidate_cm_connection()` closes pipes, resets sequence status, frees netlogon creds, and shuts down SMB clients. `close_conns_after_fork()` removes inherited sockets and client fds.

## Dependencies and Integration Points

The file integrates with libsmb transports, RPC pipe clients, generated NETLOGON/SAMR/LSA interfaces, ADS CLDAP and sitename helpers, DC discovery/namequery helpers, secrets/passdb trust credentials, `cli_credentials`, GENSEC, netlogon credential contexts, Samba messaging, gencache, server affinity and negative connection caches, idmap child messaging, and Kerberos ticket regain (`ccache_regain_all_now()`).

## Risks and Edge Cases

Authentication fallback is security-sensitive, especially anonymous fallback when configuration relaxes sealed-pipe/strong-key requirements. Stale affinity or negative cache entries can steer DC selection badly. AD DC paths sometimes ignore SMB setup because TCP RPC will be used. Domain identity mutation must reject mismatched DC-reported names/SIDs. Fork cleanup is required to avoid inherited live sockets.

## Test Signals

Test forced DC and affinity selection, negative cache skipping, AD site discovery, IP-to-name resolution failures, online/offline messaging, global offline transition, invalidation and fork cleanup, trust/IPC/anonymous auth fallback, sealed-pipe downgrade denial, SAMR/LSA/NETLOGON retry after expired sessions, current-DC gencache, and domain metadata mismatch rejection.
