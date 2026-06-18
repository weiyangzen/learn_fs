# File Research: sources/os/linux/linux-stable/fs/nfsd/xdr4cb.h

Purpose: defines static XDR buffer size estimates for NFSv4 callback RPCs issued by NFSD to clients.

Key structures and state:
- Contains only constants/macros, no structs or functions.
- Defines common sizes for callback compound headers, session IDs, referring call lists, CB_SEQUENCE encode/decode payloads, operation encode/decode headers, filehandles, and stateids.
- Defines per-callback encode/decode sizes for `CB_NULL`, `CB_RECALL`, `CB_LAYOUTRECALL`, `CB_NOTIFY_LOCK`, `CB_OFFLOAD`, `CB_RECALL_ANY`, and `CB_GETATTR`.

Major logic:
- Size formulas are expressed in XDR 32-bit words and compose shared pieces such as callback compound headers and sequence payloads.
- `CB_GETATTR` sizing accounts for bitmap, attribute array length, change/size, and atime/mtime fields.
- Offload sizing includes filehandle, stateid, write response info, and verifier.

Concurrency and lifetime:
- No runtime state or locking.
- Used to provision RPC encode/decode buffers before callback calls.

Important dependencies:
- Relies on NFSv4 constants such as `NFS4_MAX_SESSIONID_LEN`, `NFS4_FHSIZE`, `NFS4_STATEID_SIZE`, `NFS4_OPAQUE_LIMIT`, and `NFS4_VERIFIER_SIZE`.
- Consumed by `nfs4callback.c` callback operation definitions.

Risk/edge cases:
- Underestimating a size causes callback encode/decode buffer failures; overestimating wastes RPC buffer space.
- Size constants must be updated whenever callback encoders add protocol fields.
