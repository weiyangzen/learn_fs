# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_flush.c

Read completely. This file implements SMB2 `FLUSH`.

`smb2_flush()` decodes the request header fields and SMB2 file ID, requiring `StructSize == 24`. It resolves the file through `smb2sr_lookup_fid()` before DTrace start probing, then calls `smb_ofile_flush()` when lookup succeeds. On lookup or flush failure it writes an SMB2 error response; on success it encodes a structure-size-4 flush reply.

Dependencies are `smb2sr_lookup_fid()` from dispatch, `smb_ofile_flush()`, SMB mbuf helpers, and filesystem operation support through `smbsrv/smb_fsops.h`. Related-compound inherited FIDs are supported indirectly by `smb2sr_lookup_fid()`.
