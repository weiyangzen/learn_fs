# sources/user-network-fs/samba/source4/torture/raw/acls.c

Purpose: This file is a comprehensive SMB1 raw security descriptor and ACL torture suite. It tests DACL set/query behavior, security descriptors supplied at create time, null and empty DACL semantics, creator-owner handling, generic access-bit mapping, owner default rights, ACL inheritance, and dynamic inheritance expectations.

Important APIs, types, and functions: Helpers `verify_sd()` and `verify_attrib()` query `RAW_FILEINFO_SEC_DESC`, `RAW_FILEINFO_STANDARD`, and compare returned descriptors/attributes. Major tests include `test_sd()`, `test_nttrans_create_ext()`, `test_nttrans_create_ext_owner()`, `test_nttrans_create_null_dacl()`, `test_creator_sid()`, `test_generic_bits()`, `test_owner_bits()`, `test_inheritance()`, `test_inheritance_flags()`, and `test_inheritance_dynamic()`. `torture_raw_acls()` registers the suite.

Control flow: The suite repeatedly creates files or directories under `\\testsd`, applies security descriptors through `RAW_SFILEINFO_SEC_DESC` or `RAW_OPEN_NTTRANS_CREATE`, queries descriptors back, and performs access checks by reopening with specific masks. Null DACL tests distinguish a present null DACL, which grants broad access, from an empty DACL, which denies data access. Creator-owner and generic-bit tests construct descriptors with `security_descriptor_dacl_create()` and verify server-side generic-to-specific mapping. Inheritance tests iterate many ACE flag combinations, create child files/directories, and compare inherited ACE trustees, flags, and masks. Dynamic inheritance intentionally expects inherited children not to gain new parent rights after parent ACL changes.

State and persistence behavior: Every test mutates ACLs and filesystem objects under `BASEDIR`. Most paths restore original security descriptors when captured and delete the tree on exit. Some failure paths attempt cleanup but can leave modified ACLs or blocked access if interrupted.

Dependencies and integration points: The file depends on raw SMB open/fileinfo/setfileinfo, security descriptor helpers, global well-known SIDs, LSA privilege checks via `torture_check_privilege()`, SMB2-parity expectations noted in comments, and target conditionals such as `TARGET_IS_WIN7()` and `torture_setting_bool("samba4")`.

Risks: Results vary with filesystem ACL implementation, privileges such as restore and take ownership, Windows version quirks, Samba ACL defaults, and inherited SYSTEM/group ACE behavior. The file includes a disabled `GETSET` test because it does not work against XP or Vista. Cleanup can be complicated when a test successfully denies later access.

Test signals: Passing tests provide strong evidence that SMB1 security descriptor storage, DACL present/null/empty semantics, create-time ACL and owner application, access-mask reporting, generic rights mapping, inheritance flags, creator-owner substitution, and server-specific compatibility behavior remain stable.
