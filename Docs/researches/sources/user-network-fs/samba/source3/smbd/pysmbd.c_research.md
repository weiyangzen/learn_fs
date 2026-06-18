# sources/user-network-fs/samba/source3/smbd/pysmbd.c

## Purpose
This file implements the Python extension module `smbd`, exposing selected smbd VFS, NT ACL, POSIX ACL, ownership, unlink, mkdir, and create-file operations to Samba Python tooling. It lets Python code perform filesystem changes through smbd's connection, VFS, ACL, SID, and security-context machinery instead of using raw POSIX calls.

## Important APIs, Types, And Functions
The module exports `have_posix_acls`, `set_simple_acl`, `set_nt_acl`, `get_nt_acl`, `get_sys_acl`, `set_sys_acl`, `chown`, `unlink`, `mkdir`, and `create_file`. Internal helpers include `get_conn_tos`, which builds a temporary `connection_struct` for a service and `auth_session_info`; `canonicalize_path`; `init_files_struct`, which opens a path and initializes enough `files_struct` fields for VFS/ACL operations; `set_nt_acl_conn`/`get_nt_acl_conn`; `set_sys_acl_conn`; and `make_simple_acl`. `fchdir_state` restores the caller's working directory when the temporary connection wrapper is freed.

## Control Flow
Each Python wrapper validates argument types, especially `samba.dcerpc.auth.session_info` and NDR-backed security/ACL objects, creates a temporary talloc frame, obtains a smbd connection with `get_conn_tos`, converts paths into `smb_filename` or `files_struct` objects, performs the relevant VFS or ACL operation, maps NTSTATUS/errno failures into Python exceptions, and frees the frame. File and ACL operations generally open a pathref or real fd, call `SMB_VFS_*` functions, and close the `files_struct` with `fd_close`. Directory creation and unlink use parent path references plus `SMB_VFS_MKDIRAT`/`SMB_VFS_UNLINKAT`.

## State And Persistence
Runtime state is temporary and talloc-scoped, but operations persist filesystem changes: ACL updates, owner/group changes, file creation, directory creation, and unlinking. `get_conn_tos` mutates process working directory indirectly through connection setup, then relies on a talloc destructor to `fchdir` back to the saved descriptor. It also initializes POSIX locking and resets the mangle cache. Created files and directories force `umask(0)` temporarily to keep smbd in control of permissions.

## Dependencies And Integration Points
The file depends on Python C APIs, Samba `pytalloc`, NDR Python converters, auth/session structures, passdb/secrets initialization context, smbd VFS helpers, pathref helpers, POSIX ACL wrappers, NT ACL routines from the VFS, and loadparm service lookup. It is used by Samba Python administration and test code that needs smbd-equivalent ACL behavior, especially when service-specific VFS modules or security tokens matter.

## Risks And Test Signals
Risks include incomplete `files_struct` initialization relative to full smbd open paths, cwd restoration assertions in destructor paths, Python exception paths that may leak fds if close ordering changes, errno/NTSTATUS mapping inconsistencies, service lookup failures, and operations bypassing normal share read-only restrictions by explicitly setting `conn->read_only = false` and full share access. Tests should import the module, exercise each method with valid and invalid session_info, run against paths inside and outside named services, verify cwd restoration after failures, round-trip NT and POSIX ACLs, test directory vs file open fallback, confirm FileNotFoundError mapping, and validate VFS module behavior under Python-driven creates/unlinks.
