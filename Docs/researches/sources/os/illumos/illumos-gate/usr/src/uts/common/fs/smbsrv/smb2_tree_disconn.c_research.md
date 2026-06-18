# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_tree_disconn.c

Implements SMB2 tree disconnect.

Key behavior:
- Validates the fixed request structure.
- Disconnects the current tree and cancels outstanding requests for that tree.
- Encodes a minimal successful tree-disconnect response.

Important dependencies:
- `smb_tree_disconnect`, `smb_session_cancel_requests`.

Notable details:
- Dispatch is expected to have already resolved `uid_user` and `tid_tree`.
