# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_directory.c

## Role

Implements SMB1 directory create, delete, and check-directory commands, plus the common create-directory helper used by Trans2 create-directory handling.

## Major Responsibilities

- Decodes directory path operands for SMB1 directory operations.
- Rejects inappropriate operations on non-disk or IPC shares.
- Validates SMB pathnames and directory-name syntax.
- Creates directories with Windows-compatible DOS attributes.
- Deletes empty directories while enforcing DFS/root/read-only/delete-access rules.
- Verifies that a path exists, is a directory, and is traversable.
- Handles DFS link behavior for clients that set DFS flags.

## Key Functions

- `smb_pre_create_directory()` and `smb_post_create_directory()` decode and trace SMB create-directory requests.
- `smb_com_create_directory()` validates tree type/pathname and calls `smb_common_create_directory()`.
- `smb_common_create_directory()` reduces the path, checks nonexistence, enforces `FILE_ADD_SUBDIRECTORY`, sets directory attributes, calls `smb_fsop_mkdir()`, and releases nodes.
- `smb_pre_delete_directory()` and `smb_post_delete_directory()` decode and trace delete-directory requests.
- `smb_com_delete_directory()` resolves the target, rejects share roots and DFS links, requires a directory, checks DOS readonly and delete access, and calls `smb_fsop_rmdir()`.
- `smb_pre_check_directory()` and `smb_post_check_directory()` decode and trace check-directory requests.
- `smb_com_check_directory()` handles empty paths, resolves the directory, rejects non-directories, returns `PATH_NOT_COVERED` for DFS links under DFS requests, and checks `FILE_TRAVERSE`.

## Research Notes

The create path intentionally sets `FILE_ATTRIBUTE_DIRECTORY` without archive to match Windows server behavior. Delete is conservative around share roots, DFS links, readonly DOS attributes, and delete permissions.
