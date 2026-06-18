<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readdir.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readdir.c

## Purpose
Implements NFSv3 `READDIR`, producing an encoded directory entry stream with cookie verifier handling, synthetic `.` and `..` entries, FSAL directory iteration, and bounded XDR response construction.

## APIs, Types, and Functions
The important functions are `nfs3_readdir()`, `nfs3_readdir_callback()`, `nfs_readdir_dot_entry()`, and `nfs3_readdir_free()`. It uses `struct nfs3_readdir_cb_data`, `fsal_readdir()`, `fsal_lookupp()`, `xdr_encode_entry3()`, `xdrmem_create()`, `nfs_SetPostOpAttr()`, `op_ctx_export_has_option(EXPORT_OPTION_USE_COOKIE_VERIFIER)`, and `gsh_calloc()/gsh_free()`.

## Control Flow, State, and Persistence
The handler validates the directory handle, obtains directory attributes, optionally builds a cookie verifier from the directory change attribute, and validates client verifiers for nonzero cookies. It converts NFS cookies 1 and 2 into synthetic `.` and `..` responses and uses FSAL cookie 0 for real iteration when needed. The callback encodes each entry into an XDR memory buffer, checks client count and server memory limits, rewinds the XDR stream if an entry does not fit, and marks EOF only when FSAL reports end-of-directory. No filesystem state changes occur; encoded response memory is request-owned.

## Dependencies and Integration
Depends on FSAL directory enumeration semantics, NFSv3 cookie verifier export option, XDR helpers, and directory attribute `change` support. It integrates with client pagination through cookies and with the XDR response path through an `xdr_uio` buffer.

## Risks and Test Signals
Risks include cookie verifier mismatch with FSAL change support, off-by-one handling around synthetic cookies, XDR rewind correctness when entries do not fit, count limits producing `TOOSMALL` or partial replies, and memory lifetime for encoded buffers. Test signals are first-page `.`/`..`, continuation cookies, bad cookie verifier, tiny count, directory mutation between calls, no-more-entries EOF, and XDR encode failure injection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readdir.c -->
