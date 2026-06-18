# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_echo.c

## Role

Implements SMB1 Echo, used by clients to test server responsiveness without requiring a valid tree connection.

## Major Responsibilities

- Decodes requested echo count.
- Caps echo replies using `smb_max_echo`.
- Copies request data into request-scoped memory.
- Emits one SMB echo reply per requested iteration.
- Preserves request identity fields and signs replies when signing is enabled.
- Stops early if the request is cancelled.
- Returns `SDRC_NO_REPLY` because replies are sent manually.

## Key Functions

- `smb_pre_echo()` and `smb_post_echo()` provide DTrace start/done hooks.
- `smb_com_echo()` decodes the count and payload, builds each echo reply, signs as needed, sends it through the session, and delays between replies.

## Research Notes

Echo is explicitly cancellation-aware. It ignores TID semantics and manually constructs SMB headers because it may emit multiple replies for one request.
