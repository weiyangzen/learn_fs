<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_nfs4_acls.c -->
# sources/user-network-fs/samba/source3/modules/test_nfs4_acls.c

## Purpose
This is a cmocka unit-test translation unit for Samba's NFSv4 ACL conversion code. It includes `nfs4_acls.c` directly so static helpers and conversion behavior can be exercised without a loaded VFS module. The tests verify round trips and edge cases between Samba's internal `SMB4ACL_T`/`SMB_ACE4PROP_T` representation and Windows security ACL/DACL structures.

## Important APIs, Types, And Functions
The test-local `struct test_sids` table maps synthetic SIDs and creator SIDs to `struct unixid` values with `ID_TYPE_UID`, `ID_TYPE_GID`, and `ID_TYPE_BOTH`. `group_setup` parses those SIDs and seeds `idmap_cache_set_sid2unixid`; `group_teardown` removes them. Test cases target `smbacl4_nfs42win`, `smbacl4_win2nfs4`, `smb_create_smb4acl`, `smb_add_ace4`, `smb_first_ace4`, `smb_next_ace4`, `smb_get_ace4`, `smb_get_naces`, `smbacl4_get_controlflags`, and security ACL constructors such as `init_sec_ace` and `make_sec_acl`.

## Control Flow
`main` requires an `smb.conf`, initializes a talloc stack frame, loads global configuration with `lp_load_global`, and runs a cmocka group with idmap cache setup/teardown. The tests first prove the cache mappings work, then cover empty ACL conversion, ACE type mapping, inheritance and audit flag mapping, individual permission bits and generic masks, special principals, creator owner/group handling, `map_full_control`, duplicate ACE policies (`e_dontcare`, `e_reject`, `e_ignore`, `e_merge`), `e_special` mode, `ID_TYPE_BOTH` ambiguity, and duplicate removal in NFSv4-to-DACL conversion.

## State And Persistence
The only persistent external state touched is Samba's process-local idmap cache during the test group; setup inserts entries and teardown deletes them. All ACLs, SIDs, and security descriptors are talloc-owned temporary objects. The tests do not write files or durable Samba databases.

## Dependencies And Integration Points
The file depends on `nfs4_acls.c`, `librpc/gen_ndr/idmap.h`, `idmap_cache.h`, cmocka, talloc, Samba SID helpers, security descriptor helpers, and loadparm initialization. It is a direct signal for the NFSv4 ACL behavior used by NFSv4-aware VFS modules such as AIX JFS2 ACL support and by Samba's Windows ACL mapping layer.

## Risks
Because the source includes an implementation `.c` file, changes in `nfs4_acls.c` static names or dependencies can break compilation. The table-driven tests encode exact ordering, flags, and masks, so intentional semantic changes require careful test updates. `ID_TYPE_BOTH` behavior is particularly subtle because owner/group decisions change whether ACEs become user, group, or special owner/group entries.

## Test Signals
Strong signals are the 21 cmocka cases in `main`, especially the full-control, duplicate handling, `e_special`, and `ID_TYPE_BOTH` cases. A passing run with a valid `smb.conf` indicates the ACL mapper preserves expected masks, flags, SID resolution, special principal handling, and duplicate policy behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_nfs4_acls.c -->
