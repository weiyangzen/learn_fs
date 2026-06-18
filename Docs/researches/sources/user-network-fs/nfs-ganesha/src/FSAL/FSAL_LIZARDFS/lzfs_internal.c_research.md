# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/lzfs_internal.c

Purpose: Provides shared LizardFS FSAL helpers for error translation, credential context creation, static fsinfo access, handle allocation, and handle deletion.

Important APIs and types: Functions include `lizardfs2fsal_error()`, `lizardfs2nfs4_error()`, `lzfs_fsal_last_err()`, `lzfs_nfs4_last_err()`, `lzfs_fsal_create_context()`, `lzfs_fsal_staticinfo()`, `lzfs_fsal_new_handle()`, and `lzfs_fsal_delete_handle()`. It uses `struct lzfs_fsal_module`, `struct lzfs_fsal_export`, and `struct lzfs_fsal_handle`.

Control flow: Error helpers read LizardFS error codes, convert through `liz_error_conv()`, and map to FSAL or NFSv4 errors. Context creation maps anonymous export uid/gid to root uid/gid, creates a user context, and adds supplemental groups either from a stack array or heap array. Handle creation allocates and initializes an FSAL object handle, fills inode and unique key, installs object ops, sets fsid/fileid, records export pointer, and initializes a global fd for regular files.

State and persistence: The file creates in-memory handle state and contexts only. Persistent filesystem state is not modified. `lzfs_fsal_new_handle()` is the main constructor for cached Ganesha object state.

Dependencies and integration: Depends on `fsal_convert`, `pnfs_utils`, `lzfs_internal.h`, LizardFS C API, Ganesha `op_ctx`, and object/fd initialization helpers. Called by export and handle code throughout the FSAL.

Risks: In the heap supplemental-group path, memory is allocated with `gsh_malloc()` but freed with `free()`, which may mismatch allocators. Anonymous uid/gid mapping to zero is security-sensitive and must match export policy. Context creation ignores errors from `liz_update_groups()`. Handle ops are initialized per handle, so any mutable shared ops assumptions should be checked.

Test signals: Error translation for representative LizardFS errors, anonymous credential mapping, large supplemental group arrays above 64 entries, ASAN allocator mismatch checks, handle creation for every object type, and pNFS MDS ops installed only when export flag is enabled.
