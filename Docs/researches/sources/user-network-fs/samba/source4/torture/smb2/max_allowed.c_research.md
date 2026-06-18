# sources/user-network-fs/samba/source4/torture/smb2/max_allowed.c

## Purpose
`max_allowed.c` tests SMB2 `SEC_FLAG_MAXIMUM_ALLOWED` behavior, privilege-sensitive access masks, and read-only file/directory access calculations.

## Important APIs, Types, and Functions
`torture_smb2_maximum_allowed()` creates a restrictive security descriptor granting authenticated users read rights, creates `torture_maximum_allowed`, discovers the owner SID, checks restore/backup/security privileges with `torture_smb2_check_privilege()`, then iterates every single access bit combined with `SEC_FLAG_MAXIMUM_ALLOWED`. It expects success only for the computed allowed mask or maximum-allowed alone, with `NT_STATUS_PRIVILEGE_NOT_HELD` for SACL requests without privilege and `NT_STATUS_ACCESS_DENIED` otherwise. It finally restores a DACL permitting delete.

`torture_smb2_read_only_file()` and `torture_smb2_read_only_dir()` create read-only objects, open with maximum allowed and maximal-access query context, verify returned maximal and actual access masks through `RAW_FILEINFO_ACCESS_INFORMATION`, and test write/create/delete behavior. `torture_smb2_max_allowed()` registers the three subtests.

## Control Flow
The maximum-allowed test builds a known ACL baseline, records privilege capabilities for the current user, closes the original handle, then repeatedly opens the same file with `SEC_FLAG_MAXIMUM_ALLOWED | (1u << i)`. Cleanup reopens with `WRITE_DAC`, sets a delete-capable DACL, closes handles, unlinks the file, and frees the context. The read-only tests create an object, reopen it with maximum allowed, inspect effective access, and then try operations that should be denied for files or allowed inside read-only directories.

## State and Persistence Behavior
The only persistent server state is the temporary file or directory and its security descriptor/attributes; cleanup removes it. The tests intentionally mutate DACLs to make cleanup possible after restrictive setup.

## Dependencies and Integration Points
The code uses Samba security descriptor construction, SID formatting, privilege lookup helpers, SMB2 create/getinfo/setinfo utilities, and the torture `sacl_support` setting to skip SACL-related expectations where configured.

## Risks and Edge Cases
Expected masks depend on the authenticated user's privileges and server SACL support. The read-only file expected access mask follows MS-FSA rules and explicitly removes write-data, append/add-subdir, and delete-child bits; server-specific attribute enforcement can surface here. Cleanup depends on successful DACL reset.

## Test Signals
Signals include per-bit open NTSTATUS, privilege-differentiated security failures, maximal access create context values, actual access infolevel masks, denied write to a read-only file, and successful child create/delete inside a read-only directory.
