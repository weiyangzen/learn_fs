<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readdirplus.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readdirplus.c

## Purpose
Implements NFSv3 `READDIRPLUS`, extending `READDIR` by encoding attributes and file handles for each returned entry while respecting both `dircount` and `maxcount`.

## APIs, Types, and Functions
Exports `nfs3_readdirplus()`, `nfs3_readdirplus_callback()`, and `nfs3_readdirplus_free()`. It uses `struct nfs3_readdirplus_cb_data`, `fsal_readdir()`, `fsal_lookupp()`, `nfs3_FSALToFhandle()`, `xdr_encode_entryplus3()`, `xdrmem_create()`, `nfs_SetPostOpAttr()`, `EXPORT_OPTION_NO_READDIR_PLUS`, `EXPORT_OPTION_USE_COOKIE_VERIFIER`, and attribute masks `ATTRS_NFS3 | ATTR_RDATTR_ERR`.

## Control Flow, State, and Persistence
The handler rejects exports configured with no READDIRPLUS, calculates response overhead, caps memory by export `MaxRead`, validates directory type and attributes, builds/checks cookie verifier, emits synthetic `.` and `..` entries with handles/attributes, and then calls `fsal_readdir()` with a callback. The callback builds `entryplus3`, encodes the name, cookie, attributes, and post-op file handle, tracks RFC `dircount` contribution, rewinds the XDR stream if the next entry cannot fit, and frees any temporary handle allocation. Success attaches encoded data as an `xdr_uio` response and returns directory attributes and EOF state.

## Dependencies and Integration
Depends on FSAL support for per-entry object handles and attributes, NFS file-handle encoding, export limits/options, and special XDR entryplus encoders. It is a high-cost integration point between namespace traversal, attribute lookup, and handle serialization.

## Risks and Test Signals
Risks include overlarge responses from handle/attribute expansion, handle allocation leaks inside the callback, cookie verifier dependence on directory change, optional disabling via export config, and mismatches between `dircount` and `maxcount`. Test signals are normal pagination, tiny `dircount` or `maxcount`, `NO_READDIR_PLUS` exports, synthetic dot entries, handle-encoding failure, mutation causing bad cookie, and memory/XDR leak checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readdirplus.c -->
