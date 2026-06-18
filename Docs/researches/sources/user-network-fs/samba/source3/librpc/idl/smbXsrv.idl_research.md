# sources/user-network-fs/samba/source3/librpc/idl/smbXsrv.idl

## Purpose
`smbXsrv.idl` defines versioned internal state records for SMB1/SMB2 server clients, sessions, tree connects, opens, connection pass/drop messages, replay cache keys, signing/encryption state, and rolling-version coordination.

## Important APIs, types, and functions
- `smbXsrv_version_globalB` stores cluster-wide version compatibility for nodes.
- `smbXsrv_client_globalB` and `smbXsrv_clientB` model global and in-memory client state.
- `smbXsrv_connection_passB` and `smbXsrv_connection_dropB` carry connection migration/drop messages.
- `smbXsrv_session_globalB` and `smbXsrv_sessionB` store session identity, signing/encryption keys, channels, auth info, pending auth, nonces, and tree/open table links.
- `smbXsrv_tcon_globalB` and `smbXsrv_tconB` store tree connect identity, share name, signing/encryption flags, status, and compat pointer.
- `smbXsrv_open_globalB` and `smbXsrv_openB` store durable/persistent open IDs, owner, create GUID, app instance ID, backend cookie, channel sequencing, lock sequence, and request counters.
- `smbXsrv_open_replay_cache_key` and `smbXsrv_open_replay_cache` support SMB2 create replay protection.

## Control flow
The schema is organized around versioned wrappers: an outer `version` selects a union arm, currently version 0. Runtime code should operate on main structs such as `smbXsrv_session` rather than version-specific wrappers, allowing future mapping. Client/session/tcon/open records are stored, updated by sequence numbers, and passed between processes through messages as connections move or close.

## State and persistence behavior
This is core server state, partly persistent in TDB-like global databases and partly in-memory via `[ignore]` pointers. Global records include `db_record` handles, server IDs, local/global/wire IDs, timestamps, address strings, client GUIDs, auth session info, signing/encryption key blobs, channel arrays, durable open information, and replay caches. Comments state version 0 is unstable but current; a dedicated global version database prevents mixed-version cluster nodes from corrupting state.

## Dependencies and integration points
Imports include misc, server ID, security, and auth session info. Generated code builds `NDR_SMBXSRV` and integrates with smbd connection/session/tree/open tables, messaging, durable handle logic, signing/encryption, and cluster coordination.

## Risks and edge cases
This file is high-risk because schema drift can corrupt live server state. Multi-channel arrays are bounded 1..1024, key blobs are marked `noprint`, and many pointers are ignored for persistence. Version checks currently block mixed-version nodes rather than migrating records. Durable/persistent open fields, replay caches, nonce counters, and signing/encryption flags must remain consistent across reconnects and failover.

## Test signals
Test NDR round trips for version/client/session/tcon/open records, cluster mixed-version rejection, connection pass/drop messages, multi-channel session updates, signing/encryption key blob restoration, durable open reconnect, replay cache lookup, and future unknown-version decode behavior.
