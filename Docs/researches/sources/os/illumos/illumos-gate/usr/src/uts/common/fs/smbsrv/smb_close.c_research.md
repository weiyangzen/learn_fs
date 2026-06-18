# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_close.c

Implements SMB1 close and close-and-tree-disconnect commands.

Key behavior:
- Pre-decode functions read FID and optional timestamp and start DTrace probes.
- `smb_com_close()` looks up the open file, converts local timestamp to GMT, closes the ofile, and encodes an empty result.
- `smb_com_close_and_tree_disconnect()` closes the file, disconnects the tree, cancels outstanding tree requests, and encodes an empty result.
- Post handlers end DTrace probes.

Important dependencies:
- SMB1 request decode/encode: `smbsr_decode_vwv`, `smbsr_encode_empty_result`.
- File/tree/session operations: `smbsr_lookup_file`, `smb_ofile_close`, `smb_tree_disconnect`, `smb_session_cancel_requests`.
- Time conversion: `smb_time_local_to_gmt`.

Notable details:
- Failure to set requested timestamp is documented as not requiring a server error, but actual close behavior is delegated to `smb_ofile_close()`.
