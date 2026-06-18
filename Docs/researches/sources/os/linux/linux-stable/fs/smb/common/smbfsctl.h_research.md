# File Research: sources/os/linux/linux-stable/fs/smb/common/smbfsctl.h

Read status: complete.

## Purpose
Defines SMB/CIFS/SMB2 FSCTL and IOCTL control codes plus reparse tag constants shared by SMB protocol code.

## Main Contents
- FSCTL bit-layout masks for device, access, function, and method fields.
- DFS, oplock, compression, reparse point, sparse, copy offload, validate negotiate, snapshot, pipe, and network interface FSCTL codes.
- Common reparse tags including DFS, symlink, NFS, Azure File Sync, AF_UNIX, and WSL tags.
- `IS_REPARSE_TAG_NAME_SURROGATE()` and `SMB2_0_IOCTL_IS_FSCTL`.

## Dependencies And Role
Consumed by SMB IOCTL builders/parsers and reparse handling paths on both client and server sides.

## Risks
These constants are wire ABI. Incorrect values route requests to the wrong server operation or misclassify reparse points, especially around symlink/DFS/WSL behavior.
