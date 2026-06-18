# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_smb1.c

## Scope

This file implements SMB1-specific SMBFS protocol operations using classic SMB requests, TRANS2, and NT_TRANSACT.

## APIs And Behavior

- A disabled `smbfs_smb1_lockandx()` block sketches future over-the-wire locking.
- `smbfs_smb1_trans2_query()` performs query-file-information or query-path-information and decodes `SMB_QFILEINFO_ALL_INFO`.
- `smbfs_smb1_query_fs_info()` issues `SMB_TRANS2_QUERY_FS_INFORMATION`.
- `smbfs_smb1_qfsattr()` decodes filesystem attribute information.
- `smbfs_smb1_statfs()` queries size/full-size information depending on pass-through capability.
- `smbfs_smb1_flush()` sends `SMB_COM_FLUSH`.
- `smbfs_smb1_setinfo_file()` is the common TRANS2 set-file-information helper.
- `smbfs_smb1_seteof()`, `smbfs_smb1_setdisp()`, and `smbfs_smb1_setfattr()` set EOF, delete disposition, and basic metadata.
- `smbfs_smb1_t2rename()` builds same-directory `SMB_SFILEINFO_RENAME_INFORMATION` for open-file rename cases.
- `smbfs_smb1_oldrename()` sends `SMB_COM_RENAME` for cross-directory or fallback rename.
- `smbfs_smb1_trans2find2()` drives FIND_FIRST2/FIND_NEXT2, including resume keys/names, end-of-search handling, and response payload transfer to the find context.
- `smbfs_smb1_findclose2()` closes SMB1 directory search handles.
- `smbfs_smb_findopenLM2()`, `smbfs_smb_findcloseLM2()`, and `smbfs_smb_findnextLM2()` manage LM2-style directory enumeration.
- `smbfs_smb1_get_streaminfo()` queries named stream information.
- `smbfs_smb1_getsec()` gets a raw security descriptor via `NT_TRANSACT_QUERY_SECURITY_DESC`.
- `smbfs_smb1_setsec()` sets a raw security descriptor via `NT_TRANSACT_SET_SECURITY_DESC`.

## State And Dependencies

- Uses `smb_t2rq`, `smb_ntrq`, `smb_rq`, mchain/mdchain, SMB1 info-level constants, path construction, and decode helpers.

## Risks And Invariants

- SMB1 info levels vary depending on `SMB_CAP_INFOLEVEL_PASSTHRU`.
- FIND response parsing forces EOF on malformed data to avoid infinite directory loops.
- FIND close uses `SMBR_NOINTR_SEND` to avoid losing track of server search handles.
- `smbfs_smb1_setsec()` consumes the caller’s mblk chain.
