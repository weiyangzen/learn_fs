# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_ofile.c

Provides helper routines for SMB2 open-file metadata queries.

Key behavior:
- `smb2_ofile_getattr()` dispatches attribute reads to disk/printer nodes via `smb_node_getattr()` or pipe handles via `smb_opipe_getattr()`.
- `smb2_ofile_getstd()` fills delete-on-close and directory flags for `FileStandardInformation`.
- `smb2_ofile_getname()` obtains share-relative names from disk/printer nodes or pipe names and records Unicode-equivalent name length.

Important dependencies:
- `smb_node_getattr`, `smb_node_getshrpath`, `smb_node_is_dir`.
- `smb_opipe_getattr`, `smb_opipe_getname`.
- `smb_errno2status`.

Notable details:
- Pipe handles are treated as delete-on-close, non-directory objects for standard info.
- Unsupported file types return invalid device/TTY-derived errors.
