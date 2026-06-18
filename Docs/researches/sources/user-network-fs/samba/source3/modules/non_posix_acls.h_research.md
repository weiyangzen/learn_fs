# sources/user-network-fs/samba/source3/modules/non_posix_acls.h

## Purpose
Declares the non-POSIX ACL blob wrapper helper.

## APIs, Types, And Control Flow
Exports `non_posix_sys_acl_blob_get_fd_helper(vfs_handle_struct *handle, files_struct *fsp, DATA_BLOB acl_as_blob, TALLOC_CTX *mem_ctx, DATA_BLOB *blob)`. The function serializes the supplied ACL blob together with file metadata into an output blob.

## State, Dependencies, Integration
The header has no state. It relies on Samba VFS, file, talloc, and DATA_BLOB definitions from the including module. It is the interface used by non-POSIX ACL VFS code to provide ACL blob identity data.

## Risks And Test Signals
The signature passes the input blob by value and output by pointer, so callers must preserve input lifetime through serialization and manage output talloc ownership. Compile tests should include it from relevant VFS modules.
