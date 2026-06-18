# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_rename.c

Purpose: `pvfs_rename.c` implements legacy SMB rename, NT rename, hard-link, copy, stream rename, wildcard rename, open-db path updates, and notify generation for the POSIX backend.

Important APIs, types, and functions: Public functions are `pvfs_do_rename` and `pvfs_rename`. Local helpers include wildcard expansion (`pvfs_resolve_wildcard_component`, `pvfs_resolve_wildcard`), async retry (`pvfs_retry_rename`, `pvfs_rename_setup_retry`), `pvfs_rename_one`, `pvfs_rename_wildcard`, `pvfs_rename_mv`, `pvfs_rename_stream`, and `pvfs_rename_nt`.

Control flow: `pvfs_rename` dispatches by raw rename level. SMBmv-style rename resolves both patterns with wildcard support; wildcard renames list matching source entries and rename each within the same directory. Non-wildcard renames check source existence, destination absence, attribute filters, parent add-file access, and `pvfs_can_rename`, then call `pvfs_do_rename`. NT rename accepts rename, hard-link, copy, and move-cluster flags, rejecting unsupported flags and wildcard NT renames. Stream renames require a colon-prefixed target and delegate to `pvfs_stream_rename`. Sharing/oplock conflicts can install async retries through the shared ODB retry machinery.

State and persistence behavior: `pvfs_do_rename` calls `pvfs_sys_rename`, updates the open database with `odb_rename`, and emits remove/add or old-name/new-name notifications depending on whether the parent directory changed. Hard links use POSIX `link`; copy uses `pvfs_copy_file`, preserving DOS metadata through xattrs. Stream renames update stream xattr records rather than POSIX directory entries.

Dependencies and integration points: It integrates with path resolution, directory listing, access checks, open-db share checks, syscall wrappers, notify, stream helpers, file-copy utilities, and async wait callbacks.

Risks: Wildcard pattern rules are old-SMB-specific and easy to break. `pvfs_rename_one` does not preserve the lock pointer after freeing its talloc context, so lock lifetime is tied to careful flow. Cross-directory notify semantics differ from same-directory rename semantics. Hard link and copy paths do not update open-db path state in the same way as rename.

Test signals: Cover SMBmv wildcards, NT rename flags, hard-link and copy behavior, stream rename overwrite/no-overwrite, same-name no-op, destination collision, parent ACL denial, sharing violation retry, oplock-not-granted retry, and notify event ordering.
