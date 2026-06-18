# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_change_notify.c

## Purpose
SMB2 server dispatch and async completion support for `SMB2_CHANGE_NOTIFY`.

## Key Constants
- `DATA_OFF`
  - Output data offset for the SMB2 change notify response: `SMB2_HDR_SIZE + 8`.

## Key Functions
- `smb2_change_notify(...)`
  - Decodes request fields:
    - structure size
    - flags
    - output buffer length
    - file id
    - completion filter
  - Looks up the SMB2 FID.
  - Requires change notify to be last in a compound because it can block indefinitely.
  - Masks completion filter to valid bits and adds subtree watch when `SMB2_WATCH_TREE` is set.
  - Rejects output buffers larger than `smb2_max_trans`.
  - Calls `smb_notify_act1` for immediate/non-blocking event consumption.
  - If pending, moves request to async indefinite mode and calls `smb_notify_act2`.
  - If still pending, records latency before async wait and returns `SDRC_SR_KEPT`.
  - On completion/error, encodes reply data from `sr->raw_data` or emits SMB2 error.
- `smb2_change_notify_finish(...)`
  - Async completion callback dispatched by notify code.
  - Calls `smb_notify_act3` to finish common notify processing.
  - Encodes success/error response.
  - Records SMB2 stats.
  - Encodes final SMB2 header, signs if needed, sends reply.
  - Marks request completed and frees it.

## Important Interactions
- Uses shared notify state machine:
  - `smb_notify_act1`
  - `smb_notify_act2`
  - `smb_notify_act3`
- Uses SMB2 async machinery:
  - `smb2sr_go_async_indefinite`
  - `smb2_encode_header`
  - `smb2_sign_reply`
  - `smb2_send_reply`
- Handles DTrace start/done across synchronous and async completion paths.

## Notes
- The code explicitly avoids counting long async wait time as ordinary dispatch latency by sampling before going async.
