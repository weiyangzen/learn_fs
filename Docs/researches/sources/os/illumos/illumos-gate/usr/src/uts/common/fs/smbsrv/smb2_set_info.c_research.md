# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_set_info.c

Top-level SMB2 `SET_INFO` dispatcher.

Key behavior:
- Decodes info type/class, input buffer offset/length, additional info, and FID.
- Shadows the input buffer into `sinfo.si_data`.
- Rejects input buffers larger than `smb2_max_trans`.
- Looks up the FID, sets request credentials from the open file, and dispatches to file, filesystem, security, or quota set-info handlers.
- Encodes a minimal success response.

Important dependencies:
- `smb2_setinfo_file`, `smb2_setinfo_fs`, `smb2_setinfo_sec`, `smb2_setinfo_quota`.
- `smb2sr_lookup_fid`, request-scoped buffers.

Notable details:
- No output payload is expected for successful `SET_INFO`.
