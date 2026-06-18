# File Research: sources/os/linux/linux-stable/fs/nfs/callback.h

## Purpose

`callback.h` defines NFSv4 callback protocol constants, callback argument/result structures, callback process state, callback operation prototypes, and helper declarations shared by callback service, XDR, and procedure implementations.

## Main Contents

- Callback program constants: `NFS4_CALLBACK`, XDR size, and service buffer size.
- Callback procedure numbers: `CB_NULL` and `CB_COMPOUND`.
- `struct cb_process_state`, which carries the matched `nfs_client`, callback slot, network namespace, minor version, duplicate-reply-cache status, and referring-call count across operations in a compound.
- Argument/result structures for `CB_GETATTR`, `CB_RECALL`, `CB_SEQUENCE`, `CB_RECALL_ANY`, `CB_RECALL_SLOT`, `CB_LAYOUTRECALL`, `CB_NOTIFY_DEVICEID`, `CB_NOTIFY_LOCK`, and v4.2 `CB_OFFLOAD`.
- Recall-any bitmap constants for delegation and pNFS layout classes.
- Callback procedure prototypes implemented in `callback_proc.c`.
- Callback service lifecycle prototypes implemented in `callback.c`.
- Backchannel callback concurrency constants.

## Integration Points

The header ties together:

- `callback.c` service lifecycle and authentication.
- `callback_xdr.c` decoding/encoding and operation dispatch.
- `callback_proc.c` callback semantics.
- pNFS and delegation code through layout recall, device notify, recall-any, and delegation recall APIs.

## State and API Notes

`cb_process_state::clp` is always available for NFSv4.0 after `cb_ident` lookup and is set for v4.1+ by `CB_SEQUENCE`. Many callback procedures return `NFS4ERR_OP_NOT_IN_SESSION` if `clp` is absent. `cb_process_state::slot` is owned by the callback compound dispatcher after successful `CB_SEQUENCE` and must be freed after compound processing.

## Testing Focus

Review all callback operation implementations against the structures declared here, especially conditional v4.2 offload fields, recall-any mask constants, and lifetime expectations for dynamically allocated arrays in sequence and device-notify arguments.
