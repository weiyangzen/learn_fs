# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_notify_change.c

## Summary
Provides the SMB1-specific wrapper around the common change-notify engine in `smb_notify.c`.

## Main Responsibilities
- Decodes SMB1 NT transact notify setup words.
- Looks up the watched directory FID.
- Maps `WatchTree` to the internal subdirectory-change event bit.
- Calls `smb_notify_act1()` and `smb_notify_act2()`.
- Finishes async notify replies from the notify taskq.
- Builds SMB1 NT transact response framing around common notify data.

## Key APIs
- `smb_nt_transact_notify_change()`.
- `smb_nt_transact_notify_finish()`.

## Important Behavior
If `act2` parks the request, the handler returns `SDRC_SR_KEPT`; later `smb_nt_transact_notify_finish()` calls `smb_notify_act3()`, encodes a transact reply, sends it, cleans up the request, marks it completed, and frees it.

`NT_STATUS_NOTIFY_CLEANUP` is converted to a successful empty SMB1 transaction response after the watched handle closes.

The common notify code places output in `sr->raw_data`; the synchronous path swaps `raw_data` with `xa->rep_param_mb` so NT transact dispatch sees the data in the expected parameter buffer.

## Dependencies
Depends on common notify request states, SMB1 NT transact layout math, dispatcher statistics, DTrace completion probes, and `smbsr_send_reply()`/cleanup.

## Risks
The async finish function copies response-layout logic from NT transact dispatch. Changes to SMB1 transact reply framing need to be mirrored here.
