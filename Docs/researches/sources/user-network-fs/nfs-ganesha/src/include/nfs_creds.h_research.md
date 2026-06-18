# sources/user-network-fs/nfs-ganesha/src/include/nfs_creds.h

## Purpose

`nfs_creds.h` declares RPC credential extraction, comparison, squashing, and export access checks for NFS requests.

## Important APIs, Types, and Functions

Lifecycle APIs are `init_credentials` and `clean_credentials`. Request handling uses `nfs_req_creds` to populate operation context, `nfs_rpc_req2client_cred` to extract raw credential data, `nfs_compare_clientcred` for equality, `nfs4_export_check_access` for export-level access, `nfs_access_op` for object access checks, and `squash_setattr` to apply anonymous UID/GID squashing to setattr attributes.

## Control Flow

For each RPC, dispatch extracts AUTH_SYS or GSS credentials, maps them into `nfs_client_cred_t` and request context, applies export security/access policy, performs FSAL access checks, and squashes setattr ownership when export options require it.

## State and Persistence Behavior

Credential tables or helper state are initialized process-wide. Per-request credential state lives in request/op context. Squashing modifies attribute lists before they reach the FSAL; persistent effect occurs only if the FSAL setattr succeeds.

## Dependencies and Integration Points

It depends on FSAL types, SAL data, RPC request structures, export options, idmapper/GSS, and protocol handlers.

## Risks and Test Signals

Risks include trusting client-supplied groups when `Manage_Gids` should override, incorrect root/all-anonymous squashing, auth flavor mismatch, GSS principal mapping failure, and stale op context. Tests should cover AUTH_NONE/AUTH_SYS/RPCSEC_GSS, root squash variants, group list handling, export security denial, object access masks, setattr owner squashing, and credential equality edge cases.
