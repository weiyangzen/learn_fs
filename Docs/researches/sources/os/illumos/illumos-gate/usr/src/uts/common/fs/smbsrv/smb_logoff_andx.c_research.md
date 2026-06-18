# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_logoff_andx.c

This file implements SMB1 `SMB_COM_LOGOFF_ANDX`, the inverse of session setup. It logs off the SMB user referenced by the request UID.

Key responsibilities:
- Emits DTrace start/done probes for `op__LogoffX`.
- Validates that `sr->uid_user` exists.
- Calls `smb_user_logoff` to close user-owned state and invalidate the user session.
- Encodes a minimal AndX response.

Important functions:
- `smb_pre_logoff_andx` and `smb_post_logoff_andx` provide tracing hooks.
- `smb_com_logoff_andx` performs validation, user logoff, and response encoding.

Protocol behavior:
- Invalid or missing UID returns `ERRSRV/ERRbaduid`.
- Success response has WordCount 2, passes through `sr->andx_com`, and uses `-1` for the next offset.

Dependencies:
- Depends on higher-level user/session cleanup in `smb_user_logoff`.
- Response formatting is via `smbsr_encode_result`.

Edge cases:
- The file intentionally does not decode request body fields beyond relying on common SMB dispatch state.
