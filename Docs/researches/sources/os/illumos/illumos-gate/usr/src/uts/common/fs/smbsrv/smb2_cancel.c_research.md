# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_cancel.c

## Purpose
SMB2 server dispatch and immediate-reader handling for `SMB2_CANCEL`.

## Key Functions
- `smb2_newrq_cancel(...)`
  - Handles cancel requests immediately when seen in the reader path.
  - Rejects compound cancel by returning `EINVAL`.
  - Dispatches to async or sync cancel based on `SMB2_FLAGS_ASYNC_COMMAND`.
  - Sends no response.
- `smb2_cancel(...)`
  - Normal dispatch handler for cancel.
  - Drops the VC for compound cancel protocol violations.
  - Dispatches async or sync cancel.
  - Returns `SDRC_NO_REPLY`.
- `smb2_cancel_sync(...)`
  - Cancels synchronous requests by matching the cancel message ID against request credit ranges.
  - Skips cancelling itself.
  - Calls `smb_request_cancel(req)` on matches.
  - Emits DTrace error probe when match count is not one.
  - Debug builds warn when a cancel misses or races with completion.
- `smb2_cancel_async(...)`
  - Cancels async requests by matching `smb2_async_id`.
  - No response and no normal logging when count is not one because races with notify close/cancel are normal.

## Important Interactions
- Walks `session->s_req_list` under `smb_slist_enter/exit`.
- Uses request-level cancellation via `smb_request_cancel`.
- Sync cancel has inherent race with worker dispatch; async cancel is less racy because async id is known to client only after interim response.

## Notes
- SMB2 cancel never produces a protocol response.
- Compound cancel is treated as a protocol violation.
