# sources/user-network-fs/samba/source4/dsdb/tests/python/ldap.py

## Purpose

`ldap.py` is a large Samba DSDB LDAP compatibility test suite. It exercises Active Directory-like behavior exposed through Samba's `SamDB`/LDB LDAP layer: schema object-class validation, add/modify/delete/rename semantics, generated operational attributes, linked attributes, security descriptors, search controls, global-catalog visibility, RootDSE attributes, DN forms, and Windows-compatible LDAP result codes.

The file is a test executable, not a reusable library. It parses a host argument, opens a normal `SamDB` connection and, when the target is not a local `tdb://` database, a GC connection on port 3268. `TestProgram` then runs two `samba.tests.TestCase` classes: `BasicTests` for domain object behavior and `BaseDnTests` for RootDSE behavior.

## Important APIs, Types, and Functions

Key external APIs are `samba.samdb.SamDB`, `samba.Ldb`, `samba.tests.connect`-style test support through the global connections, `samba.tests.delete_force`, `samba.auth.system_session`, and LDB primitives such as `Message`, `MessageElement`, `Dn`, scopes, modify flags, and `LdbError` result codes. The test also uses DSDB constants for `userAccountControl`, `sAMAccountType`, and system flags; NDR helpers for security descriptor packing/unpacking; `security.descriptor`/SID conversion; and LSA RPC to create a secret object outside LDAP.

`BasicTests.setUp()` binds the shared connections and deletes a fixed set of `ldaptest*`, `posixuser`, container, secret, and time-value objects so each test starts from a clean domain state. `BaseDnTests.setUp()` only attaches the shared LDB handle.

Important test methods include:

- `test_objectclasses()`: structural, abstract, auxiliary, inherited, and replacement `objectClass` behavior.
- `test_system_only()`: rejects direct LDAP writes to system-only classes and attributes, including LSA-created secrets and `isCriticalSystemObject`.
- `test_invalid_parent()` and `test_invalid_attribute()`: parent existence, naming, unknown attributes, mandatory attributes, and object-class containment rules.
- `test_single_valued_attributes()`, `test_single_valued_linked_attributes()`, and `test_multivalued_attributes()`: cardinality rules and high-count multi-value modify behavior.
- `test_attribute_ranges()` and `test_attribute_ranges_too_long()`: minimum and maximum syntax/range enforcement on `sn`.
- `test_instanceType()`, `test_distinguished_name()`, and `test_rdn_name()`: protected constructed attributes, invalid DN syntax, RDN constraints, and non-writable `name`/RDN attributes.
- `test_rename()`, `test_rename_twice()`, and the large `test_all()`: normal renames, subtree renames, system-flag move restrictions, alternate DN forms, duplicate-name errors, linked-attribute repair, object category matching, ANR, UTF-8 matching, controls, and GC behavior.
- `test_objectGUID()`, `test_parentGUID()`, and `test_usnChanged()`: generated metadata and update sequencing.
- `test_linked_attributes()` and `test_wkguid()`: forward/back-link enforcement and DN+Binary matching.
- `test_security_descriptor_add()`, `test_security_descriptor_add_neg()`, and `test_security_descriptor_modify()`: SDDL and base64 security descriptor add/modify paths.
- `test_dsheuristics()`, `test_ldapControlReturn()`, `test_operational()`, `test_timevalues1()`, and the three LDAP search attribute-selection tests: controls, operational attributes, generalized time normalization, no-attribute OID, and `*`.
- `BaseDnTests` methods: RootDSE `highestCommittedUSN`, naming contexts, server paths, functionality levels, DNS hostname, and LDAP service name.

## Control Flow

At import/execution time, the script parses Samba options, credentials, subunit options, and the required host. It normalizes bare host paths/names into `tdb://` or `ldap://`, creates the domain LDB connection, optionally creates a GC connection, then launches `TestProgram`.

Each test follows a direct arrange/act/assert pattern. Most create domain entries under `CN=Users`, `CN=Computers`, or temporary containers, perform one or more LDB operations, catch `LdbError`, and assert the numeric LDAP/DSDB error code. Positive paths usually re-search by base DN or filter and verify generated attributes, canonicalized DNs, value order, or linked-attribute state. Cleanup is mostly explicit with `delete_force()` or direct `delete()`, with `setUp()` acting as an additional guard for the fixed object names.

The largest flow is `test_all()`: it builds users, groups, and computers; validates generated account fields; tests duplicate SPNs and ranged retrieval; exercises ANR filters; performs SID/GUID-based rename and delete operations; renames a subtree and verifies linked memberships update; validates UTF-8/case-insensitive searches; proves search boundary behavior with `search_options` and GC connections; and finally toggles `posixAccount` auxiliary class membership.

## State and Persistence Behavior

The tests mutate a real Samba AD database. They create users, computers, groups, containers, POSIX-style users, a system secret through LSA RPC, and temporary metadata changes such as `dSHeuristics`. Most mutations are removed explicitly; `test_dsheuristics()` saves and restores the old value in a `finally` block. Several tests rely on server-generated persistent metadata (`objectGUID`, `objectSid`, `uSNCreated`, `uSNChanged`, `whenCreated`, `whenChanged`, `parentGUID`, `memberOf`, `nTSecurityDescriptor`) and compare it across operations.

The suite uses fixed object names rather than fully random names. That makes stale state possible if a previous run aborts between setup and cleanup, but the broad `setUp()` deletion list reduces repeat-run contamination for the known names. The suite also sleeps after linked-attribute/subtree operations, implying asynchronous or delayed consistency concerns.

## Dependencies and Integration Points

This file integrates tightly with Samba's AD DC stack: the DSDB schema module, object-class module, linked-attributes module, descriptor/security code, RootDSE implementation, LDB controls (`paged_results`, `domain_scope`, `search_options`, `extended_dn`), Global Catalog search, generated operational attributes, LSA RPC, NDR security descriptor serialization, and Samba's test/subunit runner. It also relies on exact Windows-compatible numeric errors from `ldb`.

## Risks and Edge Cases

The suite is intentionally brittle about protocol compatibility: many assertions require exact result codes for invalid operations, not just failure. Any change in DSDB module order, schema refresh behavior, object-class validation, generated metadata, or control handling can alter these results.

The global `ldb`/`gc_ldb` objects and fixed names make the tests non-isolated and unsuitable for concurrent runs against the same domain. Some tests depend on timing (`time.sleep(4)`) for linked attributes, which can be slow or flaky on overloaded environments. The security descriptor tests depend on correct domain SID conversion and SDDL round-tripping. The GC path is skipped for local `tdb://` targets, so local and remote coverage differ.

## Test Signals

Passing this file signals broad LDAP compatibility for Samba AD DC. Strong signals include exact LDB error codes on invalid schema/object writes, stable generated account attributes for users/computers/groups, linked `member`/`memberOf` cleanup after delete/rename, ranged attribute retrieval correctness, security descriptor SDDL/base64 round-trip, RootDSE functionality consistency with backing objects, GC and phantom-root search behavior, and correct handling of UTF-8 and alternate SID/GUID DN forms.
