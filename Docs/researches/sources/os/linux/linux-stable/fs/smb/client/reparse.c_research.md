# File Research: sources/os/linux/linux-stable/fs/smb/client/reparse.c

This file implements CIFS/SMB reparse-point creation, parsing, and conversion into Linux inode attributes. It is the central implementation behind native Windows symlinks, NFS-style special-file reparse points, WSL/LX reparse tags, and native AF_UNIX socket tags.

Key responsibilities:
- `create_reparse_symlink()` dispatches symlink creation by mount-selected symlink type: native Windows symlink, NFS reparse, or WSL reparse.
- `create_native_symlink()` builds `IO_REPARSE_TAG_SYMLINK` buffers, converts Linux paths into SMB/NT path form when needed, handles `symlinkroot`, and sets `SYMLINK_FLAG_RELATIVE`.
- `detect_directory_symlink_target()` tries to infer whether a symlink target should be a directory symlink, using simple pathname rules first and server opens for relative targets.
- `mknod_reparse()` creates sockets, FIFOs, char/block devices, and symlinks through NFS or WSL reparse formats.
- `parse_reparse_point()` validates and parses returned reparse buffers for NFS, native symlink, WSL symlink, AF_UNIX, LX FIFO/CHR/BLK.
- `cifs_reparse_point_to_fattr()` converts parsed reparse metadata into `struct cifs_fattr` file type, mode, device, uid/gid, and dtype.

Important data paths:
- NFS-style reparse points use `IO_REPARSE_TAG_NFS` plus `NFS_SPECFILE_*` inode type values. Symlink targets are UTF-16 without trailing wide NUL; char/block devices carry two 32-bit major/minor values.
- WSL-style reparse points use `IO_REPARSE_TAG_LX_*`/`IO_REPARSE_TAG_AF_UNIX`, with `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV` EAs built during creation and consumed during fattr conversion.
- Native symlink parsing converts UTF-16 SMB targets to Linux strings, rejects embedded NULs, handles share-root-relative symlinks, and can map common absolute NT `\??\X:\...` paths back under `symlinkroot`.

Validation and error handling:
- The parser checks buffer lengths, even UTF-16 byte counts, NUL codepoints, WSL symlink version 2, mandatory device EAs for WSL char/block tags, and file-type consistency between WSL tag and `$LXMOD`.
- Unsupported tags return `-EOPNOTSUPP` unless they are directory name-surrogate/internal tags that can be represented as junction-like directories.
- Several malformed cases use `smb_EIO*()` trace helpers, which makes this file relevant for diagnostics of corrupt or malicious server reparse data.

Dependencies:
- Uses common CIFS conversion helpers, `smb2_create_ea_ctx`, SMB2 IOCTL response layout, CIFS mount flags, server operation callbacks, and definitions from `reparse.h` and `../common/smbfsctl.h`.
