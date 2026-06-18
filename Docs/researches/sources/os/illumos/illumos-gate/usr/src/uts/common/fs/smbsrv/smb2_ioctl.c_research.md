# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_ioctl.c

Read completely. This file implements SMB2 `IOCTL` request handling and dispatch to FSCTL handlers.

`smb2_ioctl()` decodes the SMB2 IOCTL fixed request, extracts control code, file ID, input/output offsets and counts, max response sizes, and flags. It shadows the input buffer when present, bounds input and output by `smb2_max_trans`, and sets `sr->raw_data` as the FSCTL output buffer.

It enforces SMB2 IOCTL rules: non-FSCTL flags return not supported; selected control codes such as DFS referrals, network interface info, validate negotiate, and pipe wait must use all-ones file IDs; all other control codes require `smb2sr_lookup_fid()` and treat lookup failure as file closed.

Dispatch is by device type extracted from `CtlCode`: DFS goes to `smb_dfs_fsctl()`, filesystem controls to `smb2_fsctl_fs()`, named pipes to `smb_opipe_fsctl()`, and network filesystem controls to `smb2_fsctl_netfs()`. Unsupported device types return not supported.

Error handling is nuanced. Normal NT error severity responses are encoded as SMB2 errors without data, but copychunk FSCTLs are allowed to return error statuses with a data payload. Successful or data-bearing responses encode the SMB2 IOCTL reply with output offset/count and raw-data payload.
