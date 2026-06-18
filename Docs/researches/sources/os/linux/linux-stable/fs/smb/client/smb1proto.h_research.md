# File Research: sources/os/linux/linux-stable/fs/smb/client/smb1proto.h

This header declares the SMB1 client API used across the CIFS client when `CONFIG_CIFS_ALLOW_INSECURE_LEGACY` is enabled.

Contents:
- `struct cifs_unix_set_info_args` carries Unix Extension set-info fields: times, mode, uid/gid, and device.
- Prototypes for SMB1 request builders and operations from `cifssmb.c`, including negotiate, tree connect/disconnect, echo, logoff, create/open/read/write/lock/close/flush, rename, hardlink/symlink, reparse-point query/create, compression, ACL, query/set path/file info, directory search, DFS referral, filesystem info, EOF/size updates, Unix info, and EA operations.
- Prototypes for files in this group:
  - `cifs_dump_detail()`
  - `cifs_sign_rqst()`
  - `cifs_verify_signature()`
  - `map_smb_to_linux_error()`
  - `smb1_init_maperror()`
  - `map_and_check_smb_error()`
  - KUnit-only maperror exports
  - `header_assemble()`
  - `is_valid_oplock_break()`
  - `smbCalcSize()`
  - `smb1_operations`
  - `smb1_values`
  - `reset_cifs_unix_caps()`
  - `CIFS_SessSetup()`
  - transport helpers such as `SendReceive*()`, request setup, message checking, and transaction validation.
- Inline helpers for SMB1 MID access/comparison and BCC/byte-area pointer handling.

Important constraints:
- All declarations are gated by `CONFIG_CIFS_ALLOW_INSECURE_LEGACY`, reflecting SMB1’s legacy/insecure status.
- `get_bcc()` and `put_bcc()` use unaligned little-endian helpers because SMB byte-count fields are computed from variable word-count offsets.

Dependency role:
- This is the cross-file contract for the SMB1 implementation; `smb1ops.c` relies on many of these declarations to populate the version operations table.
