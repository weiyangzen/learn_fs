# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_cancel.c

## Summary
Implements SMB1 `SMB_COM_NT_CANCEL`, which cancels a pending request from the same session without sending a response to the cancel command itself.

## Main Responsibilities
- Emits DTrace start/done probes.
- Searches the session request list for matching UID, PID, TID, and MID.
- Calls `smb_request_cancel()` on matching requests other than the cancel request.
- Handles cancel immediately in the SMB1 reader path.

## Key APIs
- `smb_pre_nt_cancel()`.
- `smb_post_nt_cancel()`.
- `smb_com_nt_cancel()`.
- `smb1sr_newrq_cancel()`.

## Important Behavior
The command walks `session->s_req_list` under the session list lock and cancels every matching request except itself. It expects exactly one match and emits a DTrace error probe if the match count differs. It returns `SDRC_NO_REPLY`.

`sm b1sr_newrq_cancel()` bypasses normal taskq dispatch so cancellation can hurry blocked work as early as possible.

## Dependencies
Relies on request identity fields and common `smb_request_cancel()` semantics, including the documented race between cancellation and natural request completion.

## Risks
Cancellation is inherently racy. A zero or multiple match count is observable and traced but not otherwise recoverable, and no protocol reply is sent to clarify the outcome.
