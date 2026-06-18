# File Research: sources/os/linux/linux-stable/fs/nfs/callback_xdr.c

## Purpose

`callback_xdr.c` is the NFSv4 callback XDR layer and compound dispatcher. It decodes callback RPC arguments, preprocesses operation legality by NFS minor version, invokes the semantic handlers in `callback_proc.c`, encodes per-operation and compound replies, and publishes callback service version descriptors.

## Main Responsibilities

- Decode common XDR objects: opaque strings, filehandles, bitmaps, stateids, session IDs, referring call lists, layout recall ranges, device notifications, lock owners, and v4.2 offload responses.
- Encode callback results for GETATTR and CB_SEQUENCE.
- Enforce operation legality and ordering for NFSv4.0, v4.1, and v4.2.
- Dispatch each operation in a callback compound to the appropriate decode/process/encode callbacks.
- Look up and authenticate v4.0 callback clients by `cb_ident`.
- Manage backchannel slot release after compound processing.
- Define `callback_ops[]`, callback procedure tables, and exported `svc_version` objects.

## Key Functions

- `decode_compound_hdr_arg()` decodes tag, minor version, callback identifier, and operation count, rejecting unsupported minor versions.
- `decode_op_hdr()` decodes each callback operation number and uses a special internal `NFS4ERR_RESOURCE_HDR` to distinguish header-space failures.
- `decode_getattr_args()`, `decode_recall_args()`, `decode_layoutrecall_args()`, `decode_devicenotify_args()`, `decode_cb_sequence_args()`, `decode_recallany_args()`, `decode_recallslot_args()`, `decode_notify_lock_args()`, and `decode_offload_args()` decode operation-specific arguments.
- `encode_getattr_res()` emits requested attribute bitmaps and attribute payload.
- `encode_cb_sequence_res()` emits session and slot sequencing results.
- `preprocess_nfs4_op()`, `preprocess_nfs41_op()`, and `preprocess_nfs42_op()` validate operation legality and v4.1 sequence positioning.
- `process_op()` decodes one operation, calls its handler, encodes the operation header, and encodes any successful result body.
- `nfs4_callback_compound()` decodes the compound header, resolves client/session state, loops through operations, writes compound status/count, releases callback slots, and drops the client reference.
- `nfs_callback_dispatch()` bridges SUNRPC procedure dispatch to the callback procedure table.

## Control Flow and State

The dispatcher initializes `cb_process_state` for the compound. For minor version 0, it resolves the client immediately from `cb_ident` and validates the GSS callback principal before processing operations. For minor versions 1 and 2, `CB_SEQUENCE` is required as operation zero and fills in client/session state.

Each operation follows this sequence: decode opcode, preprocess operation for the minor version, honor any duplicate-reply-cache status from `CB_SEQUENCE`, decode args into `rq_argp`, call the semantic handler into `rq_resp`, encode the operation status header, and optionally encode a response body. At compound end, the callback slot is freed and the client reference is dropped.

## Integration Points

- Calls all callback procedure functions declared in `callback.h` and implemented in `callback_proc.c`.
- Calls `check_gss_callback_principal()` from `callback.c` for v4.0 GSS callback validation.
- Uses SUNRPC server XDR streams, request argument/response buffers, and service procedure/version registration.
- Uses backchannel helpers to set callback timeout values on backchannel requests.
- Exports `nfs4_callback_version1` and `nfs4_callback_version4` for the service program in `callback.c`.

## Risks and Edge Cases

- `decode_bitmap()` reads up to three bitmap words but consumes `attrlen << 2` bytes regardless of whether more than three words are provided; only the first three are retained.
- Device notify allocation and sequence referring-call allocation must be freed on both success and decode/process error paths; this file and `callback_proc.c` split that responsibility by operation.
- `process_op()` skips operation argument decode when output buffer space is small, returning `NFS4ERR_RESOURCE`.
- `CB_SEQUENCE` duplicate uncached reply handling stores `cps->drc_status` and reports success for the sequence operation so the next operation receives the retry error.
- v4.2 support is compile-time conditional; without it, minor version 2 callbacks return minor-version mismatch.

## Testing Focus

Test malformed XDR boundaries, oversized filehandles, long tags, unsupported minor versions, illegal operations, v4.1 sequence not first, operation-not-in-session cases, device notify allocation failures, referring-call cleanup, GETATTR bitmap/result length encoding, v4.2 offload decode variants, and callback compound status/count behavior after mid-compound errors.
