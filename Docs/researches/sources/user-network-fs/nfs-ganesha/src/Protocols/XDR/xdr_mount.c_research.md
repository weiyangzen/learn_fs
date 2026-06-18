# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_mount.c

Purpose: provides rpcgen-style XDR routines for the MOUNT protocol data structures, especially MOUNT v3 status, file handles, directory paths, groups, exports, mount lists, and mount results.

Important APIs and types: `xdr_mountstat3()`, `xdr_fhandle3()`, `xdr_dirpath()`, `xdr_name()`, `xdr_groups()`, `xdr_exports()`, `xdr_mountlist()`, `xdr_mountres3_ok()`, `xdr_mountres3()`, `groupnode`, `exportnode`, `mountbody`, and `mountres3`. It uses inline helpers such as `inline_xdr_enum()`, `inline_xdr_bytes()`, and `inline_xdr_string()`.

Control flow: scalar/string wrappers serialize bounded fields. Linked-list routines encode/decode/free non-recursively: they emit a boolean presence marker, allocate or reference the node with `xdr_reference()`, and advance to the next pointer, remembering the next node during `XDR_FREE`. `xdr_mountres3()` serializes the status first and only serializes the success union arm when status is `MNT3_OK`.

State and persistence: no service state. During decode and free, XDR may allocate or release linked list nodes through the RPC runtime.

Dependencies and integration points: depends on mount/NFS protocol definitions from `nfs23.h` and file handle constants from `nfs_fh.h`. Used by mount daemon dispatch and duplicate request response cleanup through protocol free functions.

Risks: linked-list decode relies on valid remote length termination; malformed streams can fail mid-list and leave partial allocations for the caller/free path. Path and name bounds are enforced by `MNTPATHLEN`, `MNTNAMLEN`, and `NFS3_FHSIZE`. Auth flavor arrays use `XDR_ARRAY_MAXLEN`, so tests should cover very large advertised arrays.

Test signals: round-trip mount success/failure responses, export and mount lists of length zero/one/many, XDR_FREE on decoded lists, oversized names/paths/file handles, and malformed list presence markers.
