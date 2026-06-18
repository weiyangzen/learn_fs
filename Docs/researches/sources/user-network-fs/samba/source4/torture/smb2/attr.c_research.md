# sources/user-network-fs/samba/source4/torture/smb2/attr.c

## Purpose
`attr.c` implements SMB2 torture tests for DOS/Windows file attributes and security-descriptor read behavior. It checks attribute creation and truncation semantics, verifies that setting attributes does not mutate ACLs, confirms directory attribute behavior, verifies that reopening an existing file with new create attributes does not rewrite existing attributes, and validates access rules for reading security descriptors without `READ_CONTROL`.

## Important APIs, Types, And Functions
`open_attrs_table[]` enumerates normal, archive, readonly, hidden, system, and combined attribute masks used across tests. `struct trunc_open_results` and `attr_results[]` encode selected expected outcomes for overwrite/truncation combinations. `smb2_setatr()` opens a path with `SEC_FILE_READ_DATA | SEC_FILE_WRITE_ATTRIBUTE`, sends `RAW_SFILEINFO_BASIC_INFORMATION`, and closes the handle. Test entry points are `torture_smb2_openattrtest()`, `torture_smb2_winattrtest()`, `torture_smb2_winattr2()`, and `torture_smb2_sdreadtest()`. The tests use `smb2_create()`, `smb2_util_getatr()`, `smb2_util_unlink()`, `smb2_deltree()`, `smb2_getinfo_file()`, and `security_ace_equal()`.

## Control Flow
`torture_smb2_openattrtest()` iterates every initial attribute and truncation attribute combination: it creates `openattr.file`, reopens with `NTCREATEX_DISP_OVERWRITE`, expects either success with the correct final attributes or `NT_STATUS_ACCESS_DENIED`, and checks selected cases against `attr_results[]`. `torture_smb2_winattrtest()` creates a file, records its security descriptor, repeatedly sets attributes and verifies both reported attributes and unchanged ACEs, then repeats analogous checks for a directory where `FILE_ATTRIBUTE_DIRECTORY` must be present in the returned attributes. `torture_smb2_winattr2()` creates a file as archive-only, reopens with archive/system/hidden/readonly while using `OPEN_IF`, and asserts the create response still reports only archive. `torture_smb2_sdreadtest()` creates a file, reopens it with only `SEC_FILE_READ_ATTRIBUTE`, confirms security descriptor queries for owner/group/DACL are denied, then confirms a zero-bit security descriptor query succeeds but returns an empty descriptor.

## State And Persistence
Remote state consists of temporary files `openattr.file`, `winattr1.file`, `winattr2.file`, `sdread.file`, and directory `winattr1.dir`. Tests mutate DOS attributes and create/read security descriptors but do not intentionally persist changes. Cleanup resets attributes to normal where needed and unlinks or removes test paths. If a failure occurs before cleanup, readonly/hidden/system files can remain and may require attribute reset before deletion.

## Dependencies
Dependencies include SMB2 client create, setinfo, getinfo, close, unlink, deltree, and attribute helpers; raw fileinfo/setfileinfo structures; security descriptor definitions; and the SMB2 torture harness. Runtime correctness depends on server support for Windows attribute semantics, `RAW_SFILEINFO_BASIC_INFORMATION`, security descriptor queries, and expected access checks around `READ_CONTROL`.

## Integration Points
The functions are SMB2 torture test entry points declared in the SMB2 proto surface and registered elsewhere in the smbtorture SMB2 suite. They complement `acls.c`: `winattrtest` explicitly checks that DOS attribute changes preserve DACL ACEs, and `sdreadtest` validates descriptor access behavior for handles with only read-attribute rights.

## Risks
`smb2_setatr()` returns early on setinfo failure without closing the handle, which can leak a remote handle in failure paths. It also uses `tree` as the talloc context for `smb2_create()`, which is conventional in this area but ties allocations to connection lifetime. `open_attrs_table` contains adjacent `FILE_ATTRIBUTE_HIDDEN, FILE_ATTRIBUTE_SYSTEM` entries rather than a combined expression at the end, which may be intentional coverage but is visually easy to misread. `torture_smb2_openattrtest()` only has explicit expected-success table entries for selected matrix positions; unlisted success paths are not fully validated against an expected final value. Attribute cleanup can fail if the server denies resetting readonly/system attributes after an earlier failure.

## Test Signals
Strong signals are successful creation/reopen loops, expected `NT_STATUS_ACCESS_DENIED` for disallowed truncation of readonly-like states, exact final attributes for entries in `attr_results[]`, identical ACEs before and after attribute changes, directory attributes always including `FILE_ATTRIBUTE_DIRECTORY`, `winattr2` preserving archive-only attributes across `OPEN_IF`, access denied for owner/group/DACL security descriptor reads without `READ_CONTROL`, and an empty descriptor for a zero-bit security descriptor query.
