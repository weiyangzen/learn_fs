# File Research: sources/os/linux/linux/fs/nfsd/nfs3proc.c

Read completely: 1080 lines.

NFSv3 RPC procedure layer. It maps decoded request structures to nfsd VFS/filecache operations, normalizes server errors into NFSv3 status codes, and declares the NFSv3 service procedure table.

Key responsibilities:
- Implements all NFSv3 core procedures: NULL, GETATTR, SETATTR, LOOKUP, ACCESS, READLINK, READ, WRITE, CREATE, MKDIR, SYMLINK, MKNOD, REMOVE, RMDIR, RENAME, LINK, READDIR, READDIRPLUS, FSSTAT, FSINFO, PATHCONF, and COMMIT.
- Maps internal nfsd statuses to NFSv3-specific errors in `nfsd3_map_status`.
- Bounds READ and WRITE offsets/counts to `OFFSET_MAX`, service payload size, and result buffer size.
- Implements NFSv3 regular-file CREATE semantics for unchecked, guarded, and exclusive modes, including verifier-to-time conversion, existing-file handling, pre/post directory attributes, and create-time setattr.
- Initializes paged directory-list encoding buffers and recycles only pages used by READDIR/READDIRPLUS replies.
- Honors `NFSEXP_NOREADDIRPLUS` by rejecting READDIRPLUS on exports with that option.
- Reports filesystem properties, max sizes, pathconf data, and case sensitivity/preservation information.
- Uses the open-file cache for COMMIT with `nfsd_file_acquire_gc`.
- Defines the `nfsd_procedures3` table, including decode/encode/release callbacks, duplicate reply cache policy, argument/result sizes, estimated XDR sizes, names, dispatch, and counters.

Important interactions:
- Calls into `vfs.c` style helpers such as `nfsd_lookup`, `nfsd_access`, `nfsd_read`, `nfsd_write`, `nfsd_create`, `nfsd_symlink`, `nfsd_unlink`, `nfsd_rename`, `nfsd_link`, `nfsd_readdir`, `nfsd_statfs`, and `nfsd_commit`.
- Uses `filecache.c` for COMMIT open-state reuse.
- Uses `nfs3xdr.c` callbacks to encode directory entries.

Notable risks:
- Non-idempotent operations use reply-cache buffering; procedure table cache modes are part of protocol correctness.
- Exclusive CREATE verifier handling deliberately clears high bits for old Solaris and XFS bigtime compatibility.
- PATHCONF maps unexpected case-query errors to the small RFC 1813 allowed error set.
