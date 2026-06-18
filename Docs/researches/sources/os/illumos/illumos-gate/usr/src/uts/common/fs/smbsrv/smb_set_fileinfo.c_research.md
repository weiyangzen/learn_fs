# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_set_fileinfo.c

Implements SMB1/TRANS2 file and path information mutation dispatch for `smbsrv`. Entry points include `smb_com_trans2_set_file_information`, `smb_com_trans2_set_path_information`, legacy `smb_com_set_information`, and `smb_com_set_information2`.

The core split is `smb_set_by_fid` versus `smb_set_by_path`. FID updates verify writable tree state, tolerate IPC/non-disk handles as successful no-ops where protocol-compatible, look up `sr->fid_ofile`, adopt the open-file credential via `smb_ofile_getcred`, and dispatch on `sinfo.si_node`. Path updates reject read-only trees, validate and reduce the pathname, look up the target node under the share root, then dispatch and release the node.

`smb_set_fileinfo` maps information levels to concrete handlers. It handles legacy `SMB_SET_INFORMATION`, `SMB_SET_INFORMATION2`, `SMB_INFO_STANDARD`, basic/disposition/EOF/allocation/rename levels, returns `NT_STATUS_EAS_NOT_SUPPORTED` for EA set, `NT_STATUS_NOT_SUPPORTED` for link information, and `NT_STATUS_INVALID_INFO_CLASS` otherwise.

Time handling deliberately treats zero and `UINT_MAX`/`-1` as “do not change”. `smb_set_information` also preserves Windows compatibility around `FILE_ATTRIBUTE_NORMAL`: if it is the only attribute in legacy setattr, attributes are not changed. Directory attribute attempts on non-directories are rejected.

`SMB_FILE_RENAME_INFORMATION` is limited to same-directory rename semantics. It rejects nonzero `rootdir`, empty or overlong names, and names containing `\`. It builds the destination path either from the original path parent or by deriving the share path from the node parent, sets `dst_fqi` hints, and delegates to `smb_setinfo_rename`.

Primary dependencies are `smb_mbc_decodef`, `smbsr_decode_*`, pathname reduction/lookup helpers, `smb_node_setattr`, and external set-info helpers such as `smb_set_basic_info`, `smb_set_disposition_info`, `smb_set_eof_info`, and `smb_set_alloc_info`.
