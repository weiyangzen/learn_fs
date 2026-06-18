# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_trans2_dfs.c

Contains SMB1 transaction2 DFS-related handlers.

`smb_com_trans2_report_dfs_inconsistency` is intentionally unimplemented and returns `SDRC_NOT_IMPLEMENTED`, matching CIFS guidance that clients should not send the reserved command and servers should report it as not implemented.

`smb_com_trans2_get_dfs_referral` implements DFS referral lookup over IPC only. It rejects non-IPC tree connections with access denied. For valid IPC requests it builds an `smb_fsctl_t` using `FSCTL_DFS_GET_REFERRALS`, transaction input counts, maximum output response size, request parameter mbuf, and response data mbuf. It delegates referral generation to `smb_dfs_get_referrals`.

The transaction response parameter block carries an API-level DOS error code derived from the NT status. On nonzero status it also raises the SMB error with that status and DOS error; otherwise referral data is already encoded in `xa->rep_data_mb`.
