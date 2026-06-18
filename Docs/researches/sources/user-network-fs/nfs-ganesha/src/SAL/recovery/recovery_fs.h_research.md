
# sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_fs.h

## Purpose

`recovery_fs.h` exposes the reusable pieces of the filesystem recovery backend needed by newer filesystem variants. It is intentionally small: it exports current recovery path state and helper operations from `recovery_fs.c`.

## Important APIs, types, and functions

- `extern char v4_recov_dir[PATH_MAX]` and `extern unsigned int v4_recov_dir_len` expose the active recovery directory buffer and length.
- `fs_add_clid()`, `fs_rm_clid()`, and `fs_add_revoke_fh()` allow another backend to reuse legacy client directory creation/removal and revoked-handle persistence.
- `fs_clean_old_recov_dir_impl()` exposes recursive cleanup for arbitrary recovery directory roots.

## Control flow

There is no control flow in the header beyond include guarding. Its main effect is coupling `recovery_fs_ng.c` to `recovery_fs.c`: fs-ng implements a new directory-lifetime strategy but reuses the legacy record layout and per-client operations.

## State and persistence behavior

The header surfaces `v4_recov_dir` and `v4_recov_dir_len`, so callers must ensure those globals refer to the desired active directory before invoking shared helpers. For fs-ng, this means the global current directory points at the newly created temp directory rather than the stable symlink target.

## Dependencies and integration points

The declarations depend on `PATH_MAX`, `nfs_client_id_t`, and `nfs_fh4` being visible through including translation units. It integrates the old and new filesystem recovery backends by sharing the on-disk client-record format.

## Risks and edge cases

The global path exports make ordering important: if a backend calls `fs_add_clid()` before initializing `v4_recov_dir` correctly, records go to the wrong location. The header also exposes implementation details rather than an opaque context, which limits parallel use of multiple filesystem recovery instances.

## Test signals

Build coverage should ensure both `recovery_fs.c` and `recovery_fs_ng.c` can include the header in their expected include order. Runtime testing should verify fs-ng writes client directories under its temp active directory via these legacy helpers.
