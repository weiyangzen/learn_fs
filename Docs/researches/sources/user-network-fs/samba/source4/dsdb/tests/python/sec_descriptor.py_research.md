# sources/user-network-fs/samba/source4/dsdb/tests/python/sec_descriptor.py

## Purpose

`sec_descriptor.py` is a Samba AD DS integration test suite for security descriptor behavior on directory objects. It connects to a live or local `SamDB`, creates users, groups, OUs, schema classes, and configuration objects, then validates owner/group selection, DACL inheritance, `sd_flags` read/write semantics, constructed effective-rights attributes, and auto-inheritance side effects. The tests are not unit-isolated pure Python checks; they exercise Samba's LDAP/DSDB security descriptor stack, including SDDL parsing, NDR descriptor storage, ACL inheritance, and domain functional-level differences.

## Important APIs, Types, and Functions

The file uses `samba.samdb.SamDB` for directory operations, `samba.sd_utils.SDUtils` for security descriptor reads and mutation, `samba.dcerpc.security.descriptor` for SDDL-to-binary conversion, and `ndr_pack`/`ndr_unpack` for binary descriptor handling. `DescriptorTests` is the shared base class. It provides `get_users_domain_dn()`, helpers to create schema/configuration objects with optional `nTSecurityDescriptor`, `get_ldb_connection()` for non-admin user binds, and setup of `base_dn`, `configuration_dn`, `schema_dn`, `domain_sid`, and `sd_utils`.

`OwnerGroupDescriptorTests` creates eight users with different combinations of Enterprise Admins, Domain Admins, Schema Admins, and regular membership. Its large `self.results` table encodes expected `O:<owner>G:<group>` prefixes for Windows 2003-like and Windows 2008+ domain controller behavior. `DaclDescriptorTests` focuses on inherited ACE propagation. `SdFlagsDescriptorTests` validates `sd_flags` control behavior for owner, group, DACL, and SACL components. `RightsAttributesTests` validates constructed attributes `sDRightsEffective`, `allowedChildClassesEffective`, and `allowedAttributesEffective`. `SdAutoInheritTests` checks that explicit descriptor updates on parent/child OUs result in inherited ACE materialization and `uSNChanged` advancement.

## Control Flow

The module parses Samba, credential, and Subunit options, normalizes the host into `tdb://` or `ldap://`, enables sealing on credentials, and uses `TestProgram`. For remote LDAP it sets `ldb_options = ["modules:paged_searches"]` before the base class opens `SamDB`.

Each test class creates and deletes its own live directory objects. The owner/group tests run repeated patterns: bind as a test user, create an object in Domain, Schema, or Configuration naming contexts, fetch the resulting SDDL, extract the owner/group prefix with a regex, and compare it to the expected behavior table. Some tests first add creator rights to a parent DACL so a non-default principal can create children. Custom descriptor cases pass explicit SDDL or binary descriptors during object creation.

The DACL tests first create a clean protected OU by stripping inherited ACEs and setting protected flags. They then add parent ACEs with combinations of `CI`, `OI`, `IO`, `NP`, `ID`, generic rights, creator-owner SID, object attribute GUIDs, and object-class GUIDs. A child group or OU is created and the resulting SDDL is checked for exact transformed ACEs. Most tests also modify the child descriptor afterward to ensure inherited ACEs persist across descriptor rewrites.

## State and Persistence Behavior

The suite mutates persistent AD state: users, groups, OUs, schema class objects, configuration containers, display specifiers, DACLs on the schema NC root, and child security descriptors. Cleanup uses `delete_force()` and per-class `deleteAll()` methods, but failures can leave schema or configuration objects behind. Random schema class names reduce collisions but make leftover artifacts harder to inspect manually. The tests depend on domain controller functional level via `domainControllerFunctionality`, so expected owner/group SDDL changes across deployments.

## Dependencies and Integration Points

This file integrates with Samba's LDB modules, DSDB access checks, SDDL parser, NDR security descriptor representation, inherited ACL computation, object creation paths for `newuser`, `newgroup`, `create_ou`, raw LDIF adds, and LDAP controls such as `sd_flags`. It relies on well-known SIDs and constants from `samba.dcerpc.security`, `DS_DOMAIN_FUNCTION_2008`, and live membership in built-in administrative groups. It also assumes command-line credentials have enough privilege to create users, mutate schema/configuration descriptors, and read SACLs where needed.

## Risks and Edge Cases

The highest risk is environmental coupling. Tests alter security descriptors on high-value naming contexts and create schema objects; cleanup must run reliably. Several assertions are string-based SDDL exact matches, which is useful for regression coverage but sensitive to canonical ACE ordering and formatting changes. Some tests contain commented-out modify-inheritance checks marked as failing, showing known behavioral gaps. `ldb_options` is only assigned for LDAP hosts, but `DescriptorTests.setUp()` always passes it; this depends on the script's host normalization path assigning it before tests run in the exercised environments. The random schema class helper uses `self.ldb_admin.search()` rather than its `_ldb` argument when probing for collisions, which is intentional enough for admin discovery but couples helper behavior to the admin connection.

## Test Signals

Useful pass signals are exact owner/group prefixes across functional levels, preservation or removal of inherited ACEs according to Windows-compatible flag rules, correct `sd_flags` partial descriptor reads and writes, `nTSecurityDescriptor` presence only when requested or included by wildcard search semantics, effective rights changing after ACE grants, filtering read-only attributes out of `allowedAttributesEffective`, and `uSNChanged` increasing after DACL modifications. Failures here indicate regressions in authorization, descriptor canonicalization, inheritance propagation, LDAP control handling, or constructed security attributes.
