# File Research: sources/os/linux/linux/fs/nfs/callback_xdr.c

## Purpose
Implements NFSv4 callback XDR decoding, result encoding, operation admission, and COMPOUND dispatch. It is the protocol glue between SUNRPC service requests and semantic handlers in `callback_proc.c`.

## Main Responsibilities
- Decode callback COMPOUND headers and per-operation arguments.
- Encode callback COMPOUND headers and operation results.
- Enforce which callback operations are legal for NFSv4.0, v4.1, and v4.2.
- Enforce `CB_SEQUENCE` position rules for v4.1+.
- Dispatch decoded operations through a callback operation table.
- Define callback RPC procedures and service versions.

## Key Decode Functions
- `decode_compound_hdr_arg()` decodes tag, minor version, callback identifier, and operation count.
- `decode_fh()`, `decode_bitmap()`, and `decode_stateid()` decode shared protocol structures.
- `decode_getattr_args()` and `decode_recall_args()` decode v4.0 delegation callbacks.
- `decode_layoutrecall_args()` decodes file, FSID, and all-layout recalls.
- `decode_devicenotify_args()` decodes and validates pNFS device notifications.
- `decode_cb_sequence_args()` decodes session ID, sequence fields, cache flag, and referring-call lists.
- `decode_notify_lock_args()` decodes filehandle and lock owner.
- `decode_offload_args()` decodes NFSv4.2 offload completion callbacks.

## Key Encode Functions
- `encode_compound_hdr_res()` reserves status and operation-count slots and echoes the tag.
- `encode_op_hdr()` writes operation number and status.
- `encode_getattr_res()` encodes requested delegated attributes.
- `encode_cb_sequence_res()` encodes session ID, sequence ID, slot ID, highest slot ID, and target highest slot ID.
- Attribute helpers encode change, size, and time fields only when present in the response bitmap.

## Dispatch Flow
`nfs4_callback_compound()` decodes the header, resolves and authenticates v4.0 clients by callback identifier, initializes `cb_process_state`, writes the compound response header, then loops over operations with `process_op()`. After the loop it writes compound status and operation count, releases any callback slot, and drops the client reference.

## Operation Admission
- NFSv4.0 accepts only `OP_CB_GETATTR` and `OP_CB_RECALL`.
- NFSv4.1 requires `OP_CB_SEQUENCE` as the first operation and rejects later operations without it.
- NFSv4.1 accepts sequence, delegation, layout, device, recall-any, recall-slot, and notify-lock callbacks.
- NFSv4.2 additionally accepts `OP_CB_OFFLOAD` when compiled with `CONFIG_NFS_V4_2`.
- Unsupported known operations return `NFS4ERR_NOTSUPP`; unknown operations return `NFS4ERR_OP_ILLEGAL`.

## Data and Ownership
- Decoders allocate device notification arrays and referring-call lists; semantic handlers or error paths free them.
- `nfs4_cb_free_slot()` frees a locked backchannel slot after compound processing.
- v4.0 client references are acquired through `nfs4_find_client_ident()` and released at compound exit.

## Notable Details
- Uses `NFS4ERR_RESOURCE_HDR` internally to distinguish header encode/decode buffer exhaustion.
- `svc_process_common()` requires an encoder, so `nfs4_encode_void()` exists even for callback responses already encoded by the procedure.
- For invalid v4.0 credentials, the code sets `rq_auth_stat = rpc_autherr_badcred` and returns an RPC-level success accept status.
- Backchannel timeout values are copied from the resolved client RPC timeout after processing.

## Risks and Edge Cases
- `decode_bitmap()` accepts more than three bitmap words but only stores the first three after consuming all words.
- `decode_devicenotify_args()` compares `cbd_layout_type` to `NOTIFY_DEVICEID4_CHANGE` in one branch where the decoded field appears semantically to be layout type; this is a subtle area worth checking against protocol definitions.
- Response buffer admission checks `maxlen > 0 && maxlen < PAGE_SIZE`, coupling operation execution to available XDR response space.
- Many decode failures map to resource or bad XDR statuses, so callers depend on exact status semantics.

## Integration Points
Exports `nfs4_callback_version1` and `nfs4_callback_version4` consumed by `callback.c`’s `svc_program`. Dispatch entries call handlers declared in `callback.h` and implemented in `callback_proc.c`.
