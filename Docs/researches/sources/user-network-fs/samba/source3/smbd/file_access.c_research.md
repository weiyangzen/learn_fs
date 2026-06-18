# sources/user-network-fs/samba/source3/smbd/file_access.c

## Purpose
`file_access.c` implements higher-level access helpers for delete permission, write permission, default ACL inheritance detection, and delete-on-close validation.

## Important APIs, types, and functions
- `can_delete_file_in_directory()` emulates kernel delete checks against parent directory write/delete-child permissions, sticky-bit semantics, share writability, and ACL configuration.
- `can_write_to_fsp()` checks `FILE_WRITE_DATA` through `smbd_check_access_rights_fsp()`.
- `directory_has_default_acl_fsp()` scans a directory DACL for inheritable ACEs.
- `can_set_delete_on_close()` validates readonly attributes, writable share, delete access, root-of-share directories, and non-empty directory status.

## Control flow
Delete-in-directory first rejects read-only shares unless ACL checks are disabled or caller is root. If the supplied dirfsp is not the connection cwd FSP it uses that parent; otherwise it obtains a parent pathref. It verifies the parent is a directory, applies sticky-bit ownership rules, then checks `FILE_DELETE_CHILD` on the parent directory. Delete-on-close validation additionally requires the target not be readonly unless configured, the handle have `DELETE_ACCESS`, and directories be non-root and deletable via `can_delete_directory_fsp()`.

## State and persistence behavior
The file reads security descriptors and stat data but does not persist changes. It can allocate temporary pathrefs/security descriptors that are freed before return.

## Dependencies and integration points
It depends on security descriptor/VFS ACL retrieval, smbd access-right checks, pathref helpers, loadparm ACL/delete settings, and directory deletion checks from `dir.c`. Open/create/set-disposition paths use these checks before granting delete capabilities.

## Risks and edge cases
- Delete permission can come from the file's DELETE bit or parent DELETE_CHILD; this file only checks the parent-side part.
- Sticky-bit directories require owner-of-file or owner-of-directory before ACL checks can help.
- ACL check disabling and root bypass are deliberate configuration/security shortcuts.
- `can_set_delete_on_close()` calls directory emptiness checks, which can race with concurrent creates/deletes.

## Test signals
Tests should cover writable/read-only shares, ACL checks disabled, root bypass, sticky-bit owner/non-owner cases, parent DELETE_CHILD access, default ACL detection, readonly delete policy, delete access missing, root directory delete-on-close denial, and non-empty directory denial.
