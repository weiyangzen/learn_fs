# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_smb.c

## Scope

This file is the protocol-neutral SMBFS operation facade that dispatches VFS-facing operations to SMB1 or SMB2 implementations.

## APIs And Behavior

- `smbfs_smb_getfattr()` queries attributes using an existing open file handle.
- `smbfs_smb_getpattr()` queries attributes by path or temporary SMB2 attribute open.
- `smbfs_smb_qfsattr()` queries filesystem attributes and marks FAT-like shares to clamp dates before 1980.
- `smbfs_smb_statfs()` queries filesystem size info and converts it to `statvfs64_t`.
- `smbfs_smb_setdisp()` sets delete disposition.
- `smbfs_smb_setfsize()` sets end-of-file size.
- `smbfs_smb_setfattr()` builds FILE_BASIC_INFORMATION and sends DOS/time metadata updates, clamping FAT timestamps before 1980.
- `smbfs_smb_flush()` flushes an open handle.
- `smbfs_smb_ntcreatex()` builds a full SMB path and performs common create/open through `smb_smb_ntcreate()`.
- `smbfs_smb_tmpopen()` borrows an existing node FID when it has sufficient rights, otherwise opens a temporary handle.
- `smbfs_smb_tmpclose()` releases temporary or borrowed handles.
- `smbfs_smb_open()`, `smbfs_smb_close()`, and `smbfs_smb_create()` manage normal file opens/creates.
- `smbfs_smb_rename()` selects SMB2 rename, SMB1 trans2 same-directory rename, or SMB1 old rename.
- `smbfs_smb_mkdir()` creates a directory through create/open semantics and closes the temporary handle.
- `smbfs_smb_findopen()`, `smbfs_smb_findnext()`, and `smbfs_smb_findclose()` abstract directory enumeration across SMB2, SMB1, and extended attributes.
- `smbfs_smb_lookup()` implements lookup via single-entry directory enumeration.
- `smbfs_smb_getsec()` and `smbfs_smb_setsec()` dispatch raw security descriptor get/set.

## Dependencies

- Bridges SMBFS vnode code to `smbfs_smb1.c`, `smbfs_smb2.c`, extended attribute helpers, file-handle helpers, path builders, and mchain.

## Risks And Invariants

- Temporary open rights must match the operation or later SMB set/query calls fail.
- File handles include VC generation; borrowed handles are used only when generation matches.
- Directory enumeration skips `.` and `..` after UTF-8 conversion.
- Security descriptor get corrects returned length down to actual mblk payload size.
