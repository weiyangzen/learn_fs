# sources/user-network-fs/samba/source4/torture/smb2/delete-on-close.c

## Purpose

`delete-on-close.c` is a focused SMB2 torture suite for delete-on-close behavior under different create dispositions, file existence states, directory permissions, read-only attributes, directory enumeration, and a regression scenario for Samba bug 14427. It registers the `delete-on-close-perms` suite.

## Important APIs, Types, and Functions

- SMB2 create/open and cleanup APIs: `smb2_create`, `smb2_close`, `smb2_util_close`, `smb2_util_unlink`, `smb2_deltree`, `torture_smb2_testdir`, and `torture_setup_simple_file`.
- Metadata and security APIs: `smb2_getinfo_file`, `smb2_setinfo_file`, `security_descriptor_dacl_create`, `dom_sid_string`, `RAW_FILEINFO_SEC_DESC`, `RAW_SFILEINFO_SEC_DESC`, and `RAW_SFILEINFO_DISPOSITION_INFORMATION`.
- Directory enumeration APIs: `smb2_find_level` with `SMB2_FIND_BOTH_DIRECTORY_INFO`.
- Helper functions: `create_dir()` creates `test_dir` with a DACL that allows many file operations but not delete/delete-child; `set_dir_delete_perms()` reopens the directory and grants delete and delete-child permissions.

## Control Flow

Each disposition test resets permissions, removes `test_dir`, creates a controlled directory, then sends an SMB2 create for `test_dir\test_create.dat` with `NTCREATEX_OPTIONS_DELETE_ON_CLOSE | NTCREATEX_OPTIONS_NON_DIRECTORY_FILE`. The non-existing cases for `OVERWRITE_IF`, `CREATE`, and `OPEN_IF` expect `NT_STATUS_OK`, close the handle, and verify a later open returns `NT_STATUS_OBJECT_NAME_NOT_FOUND`. The existing-file cases first create the file without delete-on-close and then expect `NT_STATUS_ACCESS_DENIED` for `OVERWRITE_IF` and `OPEN_IF`, or `NT_STATUS_OBJECT_NAME_COLLISION` for `CREATE`.

`test_doc_find_and_set_doc()` opens a directory, performs a find, sets disposition delete-on-close on the directory handle, and closes it. This checks that enumeration does not prevent setting delete-on-close when permissions allow it.

`test_doc_read_only()` checks read-only interactions. It uses the `delete_readonly` torture setting to decide whether the expected status is `NT_STATUS_OK` or `NT_STATUS_CANNOT_DELETE`. It tests create-time delete-on-close for a new read-only file, delete-on-close open of an existing read-only file, and setting disposition information on an already opened read-only file.

`test_doc_bug14427()` creates a random file through one tree connection, unlinks it through a second tree connection on the same session, and verifies the unlink succeeds. The comment notes it is a regression test and not strictly delete-on-close specific.

## State and Persistence Behavior

The suite uses fixed temporary paths `test_dir` and `test_dir\test_create.dat`, plus a randomized `doc_bug14427_*.dat`. It repeatedly changes the DACL on `test_dir` to model parent directories with and without delete rights. Per-test cleanup removes `test_dir`; the bug regression also unlinks the randomized file if the second tree connection remains allocated.

Security descriptor state is important: `create_dir()` builds an inheritable ACE without `SEC_STD_DELETE` or `SEC_DIR_DELETE_CHILD`, while `set_dir_delete_perms()` grants both. The tests are validating how create disposition and delete-on-close interact with both the requested file access mask and parent directory delete rights.

## Dependencies and Integration Points

This file depends on Samba's SMB2 torture harness, security descriptor helpers, NDR security flags, and SMB2 file-information set/query APIs. The suite initializer `torture_smb2_doc_init()` registers nine tests under `delete-on-close-perms`. Runtime behavior is affected by the Samba `delete readonly` server option, exposed to the test as the `delete_readonly` torture setting.

Integration points include filesystem authorization, DACL inheritance/owner handling, disposition-information setinfo, read-only attribute semantics, directory enumeration lifetime, multi-tree unlink behavior, and SMB2 create disposition handling.

## Risks and Edge Cases

- Several tests close `io.out.file.handle` even after expected create failures; this relies on the utility close path tolerating empty or invalid handles.
- Fixed path names can conflict with parallel runs on the same share.
- Read-only expected behavior is configuration-dependent; running without the correct `delete_readonly` setting can make a valid server appear to fail.
- DACL tests assume the connected user can set owner/DACL metadata on the test directory.
- The bug 14427 test frees `tree1` before returning, which is unusual for one-tree torture tests and may matter to harness lifetime assumptions.

## Test Signals

Pass signals are exact NT status results for each create disposition/existence combination, confirmed deletion after successful delete-on-close, successful set-disposition after a directory find, expected `NT_STATUS_CANNOT_DELETE` or `NT_STATUS_OK` for read-only cases based on configuration, successful unlink through a second tree connection, and successful cleanup of the controlled directory tree.
