# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4idmap.c

This file implements NFSv4 UID/GID to owner/group string mapping and reverse mapping. It uses the kernel keyring request-key infrastructure, with a legacy rpc_pipefs upcall fallback.

Core concepts:
- `struct idmap`
  - Holds rpc pipe directory object, rpc pipe, active legacy upcall data, mutex, and user namespace.
- `id_resolver_cache`
  - Kernel credentials with a `.id_resolver` thread keyring used for idmapping key lookup.
- Two key types:
  - `id_resolver` for normal key-based resolution.
  - `id_legacy` for rpc_pipefs-driven legacy upcalls.

Attribute-name helpers:
- `nfs_fattr_init_names()` associates owner/group string storage with an `nfs_fattr`.
- `nfs_fattr_map_and_free_names()` maps owner/group names to numeric uid/gid and frees cached strings.
- `nfs_fattr_free_names()` releases owner/group strings without mapping.

Numeric shortcut:
- `nfs_map_string_to_numeric()` treats non-domain strings without `@` as numeric IDs when parseable.
- `nfs_map_numeric_to_string()` formats numeric IDs for fallback or key descriptions.

Keyring flow:
- `nfs_idmap_init()` creates `.id_resolver`, registers key types, and stores resolver credentials.
- `nfs_idmap_quit()` revokes the keyring, unregisters key types, and drops credentials.
- `nfs_idmap_get_desc()` builds descriptions like `uid:name`, `gid:name`, `user:id`, or `group:id`.
- `nfs_idmap_request_key()` first tries modern `id_resolver`; if unavailable, uses legacy `id_legacy` with aux idmap data.
- `nfs_idmap_get_key()` requests and validates a key, then copies user payload data.

Legacy rpc_pipefs flow:
- `nfs_idmap_new()` creates per-client idmap state and an `idmap` pipe under rpc_pipefs.
- `nfs_idmap_delete()` removes pipe state and releases namespace references.
- `nfs_idmap_legacy_upcall()` prepares an `idmap_msg`, queues it to the pipe, and waits for downcall completion through request-key auth.
- `idmap_pipe_downcall()` validates user response, verifies it matches the outstanding request, instantiates the key, and sets timeout.
- `idmap_release_pipe()` fails an outstanding upcall with `-EPIPE`.

Public mapping APIs:
- `nfs_map_name_to_uid()`
- `nfs_map_group_to_gid()`
- `nfs_map_uid_to_name()`
- `nfs_map_gid_to_group()`

Namespace handling:
- ID conversion uses the idmap’s user namespace if present, otherwise `init_user_ns`.
- Name-to-ID validates resulting kuid/kgid with `uid_valid()` / `gid_valid()`.
- ID-to-name falls back to numeric strings when named mapping fails or server advertises `NFS_CAP_UIDGID_NOMAP`.

Risk areas:
- Only one legacy upcall is active per idmap; `idmap_upcall_data` is protected with mutex/xchg/cmpxchg style transitions.
- Key payload length validation is strict; bad user responses become `-EINVAL` or `-ENOKEY`.
- Numeric fallback behavior affects interoperability with servers that return numeric owner strings.
