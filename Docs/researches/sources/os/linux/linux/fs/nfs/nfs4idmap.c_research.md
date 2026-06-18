# File Research: sources/os/linux/linux/fs/nfs/nfs4idmap.c

This file implements NFSv4 UID/GID to owner/group string mapping and reverse mapping. It uses the kernel request-key infrastructure, with a legacy rpc_pipefs upcall fallback.

Core concepts:
- `struct idmap` stores rpc pipe directory state, pipe data, active legacy upcall data, a mutex, and the user namespace used for ID conversion.
- `id_resolver_cache` is a kernel credential with a `.id_resolver` thread keyring used while requesting idmapping keys.
- Two key types are registered: `id_resolver` for normal key-based resolution and `id_legacy` for rpc_pipefs-driven legacy upcalls.

Attribute-name helpers:
- `nfs_fattr_init_names()` attaches owner/group string storage to an `nfs_fattr`.
- `nfs_fattr_map_and_free_names()` maps owner/group strings to numeric uid/gid and frees cached strings.
- `nfs_fattr_free_names()` releases owner/group strings without mapping.

Numeric shortcut:
- `nfs_map_string_to_numeric()` treats non-domain strings without `@` as numeric IDs when parseable.
- `nfs_map_numeric_to_string()` formats numeric IDs for fallback and key descriptions.

Keyring flow:
- `nfs_idmap_init()` creates `.id_resolver`, registers both key types, configures resolver credentials, and stores them globally.
- `nfs_idmap_quit()` revokes the keyring, unregisters key types, and drops credentials.
- `nfs_idmap_get_desc()` builds descriptions such as `uid:name`, `gid:name`, `user:id`, or `group:id`.
- `nfs_idmap_request_key()` first tries the modern `id_resolver` in init user namespace cases, then falls back to legacy `id_legacy` with the per-client idmap as aux data.
- `nfs_idmap_get_key()` validates a key and copies its user payload into the caller buffer.

Legacy rpc_pipefs flow:
- `nfs_idmap_new()` creates per-client idmap state and an `idmap` pipe under rpc_pipefs.
- `nfs_idmap_delete()` removes the pipe object, destroys pipe data, releases the user namespace, and frees idmap state.
- `nfs_idmap_legacy_upcall()` prepares an `idmap_msg`, records one active upcall, queues it to the pipe, and completes request-key auth on failure or later downcall.
- `idmap_pipe_downcall()` validates the userspace response, checks it matches the outstanding request, instantiates the target key, sets cache timeout, and returns the downcall byte count.
- `idmap_release_pipe()` fails an outstanding upcall with `-EPIPE`.

Public mapping APIs:
- `nfs_map_name_to_uid()` maps owner names to `kuid_t`, using numeric shortcut or key lookup and validating with `uid_valid()`.
- `nfs_map_group_to_gid()` maps group names to `kgid_t`, using numeric shortcut or key lookup and validating with `gid_valid()`.
- `nfs_map_uid_to_name()` maps `kuid_t` to owner string, falling back to numeric output when named mapping fails or `NFS_CAP_UIDGID_NOMAP` is set.
- `nfs_map_gid_to_group()` maps `kgid_t` to group string with the same fallback behavior.

Namespace handling:
- ID conversion uses the idmap's user namespace if available, otherwise `init_user_ns`.
- Reverse mapping uses `from_kuid_munged()` / `from_kgid_munged()`.

Risk areas:
- Only one legacy upcall is active per idmap; `idmap_upcall_data` transitions use mutex, `xchg()`, and `cmpxchg()` patterns.
- Key payload length and userspace downcall validation are strict; malformed responses become `-EINVAL`, `-ENOKEY`, `-ENOSPC`, or `-EFAULT`.
- Numeric fallback behavior affects interoperability with servers that return numeric owner/group strings.
