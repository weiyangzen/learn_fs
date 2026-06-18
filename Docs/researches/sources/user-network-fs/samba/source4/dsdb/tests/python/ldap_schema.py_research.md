# sources/user-network-fs/samba/source4/dsdb/tests/python/ldap_schema.py

## Purpose

`ldap_schema.py` is a Samba AD schema behavior test suite. It verifies that schema reads, schema updates, generated schema attributes, custom attributes/classes, uniqueness constraints, generated IDs, and constructed RODC-related attributes behave like Active Directory over LDAP.

The suite creates real `attributeSchema` and `classSchema` objects in the schema naming context, triggers schema refresh with RootDSE `schemaUpdateNow`, then searches or instantiates objects to prove the schema changes are active.

## Important APIs, Types, and Functions

The file uses `SamDB` connections with optional `modules:paged_searches` for remote LDAP targets, `system_session`, LDB scopes/errors/messages, `delete_force`, DS functional-level constants, and NDR unpacking of `drsblobs.replPropertyMetaDataBlob`.

`SchemaTests` covers general schema behavior:

- `test_generated_schema()` and `test_generated_schema_is_operational()` verify `cn=aggregate` generated schema attributes are returned only when requested.
- `test_schemaUpdateNow()` creates a custom attribute and class, rejects an invalid `defaultObjectCategory`, forces schema refresh, instantiates the class, and checks replication metadata contains the generated `msDS-IntId` attid when applicable.
- `test_subClassOf()` creates a custom class derived from `organizationalUnit` and instantiates it.
- Duplicate/immutability tests cover `attributeID`, `governsID`, `cn`, implicit/explicit `ldapDisplayName`, rename-to-duplicate, removing/renaming `ldapDisplayName`, and changing `attributeID`/`governsID`.
- `test_generated_linkID()` verifies automatic linkID generation, uniqueness, forward/back-link pairing, and rejection of duplicate or invalid backlink definitions.
- `test_generated_mAPIID()` verifies automatic mAPIID generation and duplicate rejection.

`SchemaTests_msDS_IntId` focuses on `msDS-IntId` rules. Helpers `_ldap_schemaUpdateNow()`, `_make_obj_names()`, `_is_schema_base_object()`, `_make_attr_ldif()`, and `_make_class_ldif()` generate schema LDIF and inspect `systemFlags`. Tests verify whether attributes/classes may set or modify `msDS-IntId`, and whether non-base attributes receive it at sufficient forest functional level.

`SchemaTests_msDS_isRODC` searches existing `nTDSDSA`, `server`, and `computer` objects with the phantom-root-style `search_options:1:2` control and checks that `msDS-isRODC` is present when a corresponding NTDS settings/server-reference relationship exists.

## Control Flow

At startup, the script parses options, credentials, and host. It normalizes the host scheme and chooses `ldb_options`; remote LDAP gets paged-search modules. `TestProgram` runs the three test classes.

Each test method opens or reuses a `SamDB` connection in `setUp()`, discovers `base_dn` and `schema_dn`, builds LDIF strings with timestamp/random OID suffixes, and performs `add_ldif()`, `modify_ldif()`, `modify()`, and `search()` calls. Negative tests catch `LdbError` and assert exact codes such as `ERR_UNWILLING_TO_PERFORM`, `ERR_CONSTRAINT_VIOLATION`, `ERR_ENTRY_ALREADY_EXISTS`, `ERR_OBJECT_CLASS_VIOLATION`, or `ERR_NO_SUCH_OBJECT`.

Schema activation is explicit in tests that need immediate use of new definitions: they modify RootDSE with `schemaUpdateNow: 1`, then instantiate objects or search generated IDs.

## State and Persistence Behavior

These tests persistently add schema objects to the target directory. Most schema objects are named with `time.strftime("%s")` plus random OID components, reducing collisions but leaving schema extensions behind because schema entries cannot generally be deleted like normal test objects. Some domain objects instantiated from new schema classes are deleted after validation.

Generated persistent state under test includes `lDAPDisplayName`, `defaultObjectCategory`, `schemaIDGUID`, `msDS-IntId`, `linkID`, `mAPIID`, and replication metadata. Functional level affects expected `msDS-IntId` and linkID behavior; tests read RootDSE `forestFunctionality` or `domainControllerFunctionality` before deciding expectations or skipping.

## Dependencies and Integration Points

The file integrates with the DSDB schema loader/cache, RootDSE schema refresh, generated schema aggregate, OID uniqueness enforcement, `schemaIDGUID` generation, replication metadata encoding, prefix-map/attid behavior, functional-level gates, linked-attribute schema rules, paged LDAP searches, and constructed `msDS-isRODC` logic across server/computer/NTDS settings objects.

## Risks and Edge Cases

Because schema additions are durable and use random suffixes, repeated runs can grow the schema. Tests that assert exact errors are sensitive to validation ordering. Time-based names only have second resolution, so rapid concurrent runs still need the random OID portions to avoid collisions; names without random suffix in some tests may collide if parallelized in the same second. Functional-level differences intentionally change expectations, and comments note Windows refresh behavior requiring explicit schema update. `test_verify_msDS_IntId()` prints warnings for missing IDs rather than failing in some cases, so it is partly diagnostic.

## Test Signals

Passing this suite indicates Samba can expose generated schema over LDAP, accept valid custom attributes/classes, reject duplicate or illegal schema identity changes, refresh schema for immediate use, generate and protect `msDS-IntId`, `linkID`, and `mAPIID` correctly, and construct `msDS-isRODC` on relevant directory objects. Failure usually points to DSDB schema validation, generated-ID allocation, RootDSE refresh, functional-level handling, or constructed-attribute regressions.
