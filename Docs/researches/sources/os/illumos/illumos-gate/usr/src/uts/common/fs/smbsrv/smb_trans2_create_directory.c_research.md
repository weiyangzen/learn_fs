# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_trans2_create_directory.c

Implements `TRANS2_CREATE_DIRECTORY`, the SMB1 transaction2 directory-create subcommand. It accepts a reserved field, directory name, and optional FEA list, though the implementation only returns an EA error offset of zero.

`smb_com_trans2_create_directory` requires a disk tree, decodes the pathname from the transaction parameter block, initializes and validates the pathname, performs directory-name-specific validation, then delegates creation to `smb_common_create_directory`. Filesystem errors are translated with `smbsr_errno`.

On success it encodes a single zero `EaErrorOffset` in the transaction response parameter block and returns `SDRC_SUCCESS`. IPC or non-disk shares are rejected with access denied.
