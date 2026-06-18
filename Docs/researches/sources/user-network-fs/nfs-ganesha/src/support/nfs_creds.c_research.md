# sources/user-network-fs/nfs-ganesha/src/support/nfs_creds.c

## Purpose
This file builds request credentials in `op_ctx`, applies export security policy, performs root/all squash handling, resolves managed groups, compares RPC credentials, and provides a version-independent ACCESS helper.

## Important APIs, Types, And Functions
Global masks `root_op_export_options` and `root_op_export_set` describe root context export permission fields. Public functions include `squash_setattr`, `nfs_compare_clientcred`, `nfs_rpc_req2client_cred`, `nfs_req_creds`, `init_credentials`, `clean_credentials`, `nfs4_export_check_access`, and `nfs_access_op`. Internal helpers `set_extended_groups`, `rpcsec_gss_fetch_managed_groups`, and `squash_creds` coordinate group lookup and credential rewriting.

## Control Flow
`nfs4_export_check_access` refreshes export permissions, validates access mask, NFSv4 protocol enablement, transport, privileged port policy, and security flavor, then calls `nfs_req_creds`. `nfs_req_creds` parses AUTH_NONE, AUTH_SYS, or RPCSEC_GSS credentials, maps GSS principals to uid/gid when enabled, fetches managed groups, calls `set_extended_groups`, then applies anonymous/root squashing in `squash_creds`. `nfs_access_op` translates ACCESS3/ACCESS4 bits into FSAL mode and ACE masks, calls `obj_ops->test_access`, and maps allowed bits back to protocol response masks while honoring read-only exports.

## State And Persistence
Most state is per-request in `op_ctx`: original credentials, active credentials, group data references, copied group arrays, export permission flags, and squash flags. `clean_credentials` releases temporary group references/copies and resets credential state. There is no durable persistence.

## Dependencies And Integration Points
The file integrates with TI-RPC request structures, optional GSSAPI, idmapper/principal mapping, `uid2grp`, export manager/client manager, FSAL export/object operations, LTTng tracepoints, monitoring counters, and NFSv4 protocol access checks.

## Risks And Test Signals
Risks include explicit reliance on TI-RPC private structures, complex flag interactions among `CREDS_LOADED`, `CREDS_ANON`, `MANAGED_GIDS`, and squash flags, fallback behavior controlled by `enable_rpc_cred_fallback`, truncation of long GSS principals to `MAXNAMLEN`, and subtle group-array ownership rules. Tests should cover AUTH_NONE, AUTH_SYS, RPCSEC_GSS success/failure, managed group fallback on/off, all squash/root squash/root-id squash, root group squashing in supplemental groups, read-only export ACCESS filtering, transport/protocol rejection, and `clean_credentials` leak checks.
