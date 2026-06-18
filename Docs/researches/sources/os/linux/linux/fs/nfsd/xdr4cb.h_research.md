# File Research: sources/os/linux/linux/fs/nfsd/xdr4cb.h

`xdr4cb.h` defines static XDR size estimates for NFSv4 callback requests and replies. These constants are used by callback encode/decode paths to size RPC buffers for backchannel operations.

The file defines:
- Compound callback header sizes and max callback tag length.
- Sessionid and referring-call list word sizes for `CB_SEQUENCE`.
- Common op encode/decode sizes.
- Filehandle and stateid encoded sizes.
- Per-callback size macros for `CB_RECALL`, `CB_LAYOUTRECALL`, `CB_NOTIFY_LOCK`, `CB_OFFLOAD`, `CB_RECALL_ANY`, and `CB_GETATTR`.

The comments for `CB_GETATTR` document the exact expected fields: opcode, filehandle, attribute bitmap array, fattr length, change, size, atime, and mtime components. The header is purely declarative and depends on NFSv4 constants such as `NFS4_MAX_SESSIONID_LEN`, `NFS4_FHSIZE`, `NFS4_STATEID_SIZE`, `NFS4_OPAQUE_LIMIT`, and `NFS4_VERIFIER_SIZE`.
