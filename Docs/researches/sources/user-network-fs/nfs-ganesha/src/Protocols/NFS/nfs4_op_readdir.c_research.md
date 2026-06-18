# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_readdir.c

## Purpose
Implements NFSv4 READDIR, including attribute encoding for directory entries, cookie-verifier handling, response-size limiting, dircount byte-budget enforcement, junction traversal for nested exports, and RDMA-aware serialized XDR result buffers.

## Important APIs, Types, and Functions
- `struct nfs4_readdir_cb_data` tracks the XDR stream, entry buffer, maxcount, dircount accounting, requested attributes, compound data, error state, and saved export context used during junction traversal.
- `nfs4_op_readdir` is the public handler.
- `nfs4_readdir_callback` is passed to `fsal_readdir` and encodes each `entry4` or error attribute record into the preallocated XDR memory buffer.
- `restore_data` restores `op_ctx` export and request credentials after a junction traversal or failure.
- `xdr_dirlist4_uio_release` releases the response UIO buffers when XDR no longer references them.

## Control Flow
The handler validates CurrentFH as a directory, derives `maxcount` from session response room, configured readdir response size, and client `maxcount`, rejects reserved cookies 1 and 2, validates and filters requested attributes, optionally builds a cookie verifier from the directory change attribute, allocates the entries buffer, creates an XDR memory stream, and calls `fsal_readdir`. The callback accounts for base entry size, encoded filename size, and dircount bytes; optionally crosses junction exports to gather attributes from the target export root; handles WRONGSEC, ACCESS, MOVED, and RDATTR_ERROR; temporarily swaps `data->current_obj` to encode filesystem attributes; and rolls the XDR stream back when an entry cannot fit.

After `fsal_readdir`, the handler converts tracker errors, writes final `entry_follows`/EOF booleans, wraps the encoded byte range in `struct xdr_uio`, transfers buffer ownership to the response, copies the cookie verifier, and destroys the XDR stream. If no entry fit, it returns EOF state directly in `reply.eof`.

## State and Persistence Behavior
READDIR does not persist filesystem state, but it mutates transient compound context while crossing junctions and while encoding attributes. The callback saves and restores export context and credentials. The response buffer is handed off by setting `tracker.entries = NULL`; free behavior is tied to UIO release and RDMA buffer usage. Cookie verifier state is derived from the directory change attribute when the export option enables it.

## Dependencies and Integration Points
Depends on FSAL readdir and object access checks, export manager junction fields (`junction_export`, `jct_lock`), credential rebuilding through `nfs_req_creds`, attribute/XDR helpers (`bitmap4_to_attrmask_t`, `xdr_encode_entry4`, `xdr_nfs4_fattr_fill_error`), response sizing, and RDMA buffer helpers. It is tightly integrated with pseudo export behavior because READDIR must present junction entries with the same filehandle and attributes that LOOKUP would expose.

## Risks
- Junction traversal lock and export-reference ordering is delicate; failure to restore context can leak credentials/export state into later compound operations.
- Buffer rollback must encode a false `entry_follows`; XDR position mistakes can corrupt the directory list.
- `dircount` is enforced as cookie plus XDR name bytes, while `maxcount` limits the whole serialized response; regressions here affect client pagination.
- Requested attribute combinations around WRONGSEC, RDATTR_ERROR, FS_LOCATIONS, and MOUNTED_ON_FILEID need protocol-specific handling.
- UIO allocation size and RDMA buffer ownership must match release expectations.

## Test Signals
Test empty directories, one-entry and many-entry pagination, cookie 1/2 rejection, cookie-verifier mismatch, `maxcount` too small, `dircount` limiting after some entries, long names, unsupported or unreadable attributes, ACL attribute access failures, referrals and junctions, WRONGSEC with and without allowed attrs, RDMA buffer responses, and repeated READDIR pages where cookies and EOF remain stable.
