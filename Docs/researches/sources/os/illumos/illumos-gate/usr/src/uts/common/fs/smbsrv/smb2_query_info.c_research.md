# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_query_info.c

Top-level SMB2 `QUERY_INFO` dispatcher.

Key behavior:
- Decodes fixed request fields, output length, optional input buffer, additional info, flags, and FID.
- Caps output by `smb2_max_trans` and uses `sr->raw_data` as the response payload buffer.
- Looks up the FID and dispatches to file, filesystem, security, or quota query handlers.
- Encodes successful responses with data offset and length.
- Special-cases advisory `NT_STATUS_BUFFER_OVERFLOW`.
- Formats `NT_STATUS_BUFFER_TOO_SMALL` and `NT_STATUS_INFO_LENGTH_MISMATCH` differently for SMB 3.1.1 error context behavior.

Important dependencies:
- `smb2_qinfo_file`, `smb2_qinfo_fs`, `smb2_qinfo_sec`, `smb2_qinfo_quota`.
- `MBC_SHADOW_CHAIN`, `smb2sr_lookup_fid`, `smb2sr_put_error*`.

Notable details:
- Security-descriptor buffer-too-small is expected to carry required-size data.
