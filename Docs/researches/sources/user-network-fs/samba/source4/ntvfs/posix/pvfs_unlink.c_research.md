# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_unlink.c

Purpose: `pvfs_unlink.c` implements file and stream deletion for the POSIX backend, including wildcard deletes, attribute filtering, share-mode checks, async retry on sharing/oplock conflicts, xattr cleanup, and notify events.

Important APIs, types, and functions: The public entry point is `pvfs_unlink`. Local helpers are `pvfs_retry_unlink`, `pvfs_unlink_setup_retry`, `pvfs_unlink_file`, and `pvfs_unlink_one`.

Control flow: `pvfs_unlink` resolves the requested pattern with wildcard, stream, and no-open-db flags. It rejects absent non-wildcard names and directory targets, then either deletes one resolved object or starts a directory listing for wildcard deletes. Wildcard deletes disable async retry until properly tested, iterate matching entries, reject dot entries when directory attributes are involved, resolve each entry partially, and call `pvfs_unlink_one`. `pvfs_unlink_one` enforces attribute filters, calls `pvfs_can_delete` to check open-db share and delete rights, optionally installs async retry, then deletes a stream through `pvfs_stream_delete` or a normal file through `pvfs_unlink_file`.

State and persistence behavior: Normal file deletion removes EADB/system xattrs through `pvfs_xattr_unlink_hook` when the file has a single link, calls `pvfs_sys_unlink`, and emits file-name removal notifications. Stream deletion updates stream xattrs and the stream index. Open-db state is consulted, not directly mutated except through retry registration.

Dependencies and integration points: It depends on name resolution, directory listing, attribute matching, delete/share checks in `pvfs_open.c`, async wait/retry infrastructure, stream deletion, xattr cleanup, syscall wrappers, and notify.

Risks: Wildcard deletion deliberately disables async behavior, so sharing conflicts in a batch may produce partial progress. Xattr cleanup only runs at link count one, which is correct for hard links but important to preserve. Directory deletion is not handled here. Error status after wildcard operations is the last failure unless at least one delete succeeds.

Test signals: Cover single file delete, stream delete, wildcard delete with partial failures, hidden/system/directory attribute filters, dot entry rejection, sharing violation retry, oplock-not-granted retry, hard-link xattr retention, notify emission, and permission override behavior.
