# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_cmn_setfile.c

This file implements common SMB1 Trans2 and SMB2 set-file information handlers for basic metadata, end-of-file size, allocation size, and delete-on-close disposition. The handlers decode wire data from `smb_setinfo_t.si_data`, validate SMB/FSCC semantics, break relevant oplocks when the operation changes data or handle caching, then apply attributes through node-level filesystem helpers.

Public entry points are `smb_set_basic_info`, `smb_set_eof_info`, `smb_set_alloc_info`, and `smb_set_disposition_info`.

`smb_set_basic_info` decodes `FileBasicInformation` times and attributes. It rejects temporary attributes on directories and directory attributes on non-directories. Nonzero timestamp fields are converted from NT time to Unix time and placed into `smb_attr_t`; negative special values less than `-2` are invalid. Attribute handling follows Windows compatibility: zero means no attribute update, while a nonzero value is set as DOS attributes through `SMB_AT_DOSATTR`. The final update goes through `smb_node_setattr` with the request user's credential and current ofile.

`smb_set_eof_info` decodes a 64-bit EOF, rejects directories, breaks `FileEndOfFileInformation` oplocks with `smb_oplock_break_SETINFO`, optionally moves SMB2 requests async while waiting, and then sets `SMB_AT_SIZE` through `smb_node_setattr`. `smb_set_alloc_info` is structurally the same but uses `FileAllocationInformation` and writes `SMB_AT_ALLOCSZ`.

`smb_set_disposition_info` toggles delete-on-close for the open file. It requires a real ofile and `DELETE` granted access. Clearing disposition resets the node delete-on-close state immediately. Setting disposition checks the current DOS readonly attribute with `smb2_ofile_getattr` and returns `NT_STATUS_CANNOT_DELETE` if readonly, breaks handle-caching oplocks for `FileDispositionInformation`, waits as needed, and then calls `smb_node_set_delete_on_close`. CATIA tree support is propagated through flags.

Integration notes: EOF and allocation changes are data-affecting and must not bypass oplock breaks. Disposition handling distinguishes ofile state from node delete-on-close state and follows documented Windows 2000 behavior. All functions return NT status values rather than SMB dispatch result codes.
