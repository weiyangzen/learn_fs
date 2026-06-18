<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/smb2.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/smb2.c

Purpose: supplies SMB2 composite helpers that emulate common SMB1 path operations requiring multiple SMB2 requests: unlink, mkdir, rmdir, and setpathinfo.

Important APIs and types: `smb2_composite_unlink_send`, `smb2_composite_unlink`, `smb2_composite_mkdir_send`, `smb2_composite_mkdir`, `smb2_composite_rmdir_send`, `smb2_composite_rmdir`, `smb2_composite_setpathinfo_send`, `smb2_composite_setpathinfo_recv`, and `smb2_composite_setpathinfo`. Internal state tracks delete/truncate handles and setpathinfo create/set/close status.

Control flow: unlink rejects wildcard patterns, opens the path with delete-on-close and optional write-data access, optionally truncates non-empty files, then closes. mkdir creates a directory and closes the handle. rmdir opens a directory with delete-on-close and closes. setpathinfo opens a path, sets file info by handle, closes, and returns the setinfo status ahead of close status.

State and persistence: remote state changes are actual path deletion, directory creation/deletion, and metadata updates. Handles are carried in state until close. The sync setpathinfo wrapper uses a stack talloc frame and polls the tevent request.

Risks: unlink intentionally ignores truncate errors to avoid handle leaks, so callers may see close/delete status rather than truncation detail. Path normalization strips one leading backslash by incrementing the pointer. Test signals include wildcard rejection, delete-on-close semantics, truncate-if-needed behavior on non-empty files, close-after-setinfo on failure, and correct status priority between setinfo and close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/smb2.c -->
