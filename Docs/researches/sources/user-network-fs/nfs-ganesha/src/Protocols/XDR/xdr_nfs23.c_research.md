# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nfs23.c

Purpose: implements hand-maintained XDR routines for NFSv2 and NFSv3 wire types, including scalar wrappers, file handles, attributes, weak cache consistency data, all major NFSv3 operation arguments/results, read/write payloads, and optimized directory listing encoders.

Important APIs and types: NFSv2 helpers such as `xdr_nfspath2()`, `xdr_fhandle2()`, `xdr_nfsdata2()`; NFSv3 helpers such as `xdr_nfs_fh3()`, `xdr_fattr3()`, `xdr_sattr3()`, `xdr_wcc_data()`, and per-operation functions for `GETATTR`, `SETATTR`, `LOOKUP`, `ACCESS`, `READ`, `WRITE`, `CREATE`, `MKDIR`, `SYMLINK`, `MKNOD`, `REMOVE`, `RMDIR`, `RENAME`, `LINK`, `READDIR`, `READDIRPLUS`, `FSSTAT`, `FSINFO`, `PATHCONF`, and `COMMIT`. It also exports `xdr_encode_entry3()`, `xdr_encode_entryplus3()`, `xdr_dirlist3_uio_release()`, and `xdr_dirlistplus3_uio_release()`.

Control flow: most routines serialize fields in protocol order and switch on status or discriminator fields before handling union arms. `xdr_fattr3()` translates between FSAL internal file types/modes and NFSv3 `ftype3`/Unix mode on encode/decode. Request argument decoders update `struct nfs_request_lookahead` through `xdrs->x_public` for read, write, create, remove, rename, readdir, and commit so upper layers can make cacheability and scheduling decisions. Directory response handling supports normal linked-list XDR and a zero-copy-ish `xdr_uio` path through `xdr_putbufs()`.

State and persistence: no durable state. It mutates decoded structures, request lookahead counters, and `xdr_uio` reference counts. UIO release avoids freeing RDMA buffers when `op_ctx->is_rdma_buff_used` is set.

Dependencies and integration points: depends on `nfs23.h`, FSAL attribute conversion helpers, file handle definitions, `op_ctx`, `gsh_free`, and ntirpc XDR extensions. Duplicate request cache logic consumes lookahead flags produced here, especially to decide NFSv4 duplicate caching behavior.

Risks: attribute type conversion logs bogus values but may continue with partially initialized locals for unexpected types. Directory UIO reference/release behavior must match async send completion; premature or missing release leaks or double-frees buffers. Bounds for NFSv3 strings use `XDR_STRING_MAXLEN`, while file handles cap at 64 bytes. Lookahead updates depend on `xdrs->x_public` having the expected layout.

Test signals: XDR round trips for every NFSv3 operation success/failure union, fattr encode/decode for all file types, read/write payloads, readdir/readdirplus linked-list and UIO encodings, RDMA buffer release behavior, and lookahead flag/counter assertions after decoding relevant operations.
