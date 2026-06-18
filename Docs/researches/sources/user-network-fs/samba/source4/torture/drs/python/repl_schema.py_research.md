# sources/user-network-fs/samba/source4/torture/drs/python/repl_schema.py

## Purpose
`repl_schema.py` tests schema naming-context replication between two writable DCs. It dynamically creates `classSchema` and `attributeSchema` objects, forces schema and domain replication, and verifies that schema cache updates, custom attributes, linked attributes, binary DN links, inheritance, and renames replicate correctly.

## Important APIs, Types, And Functions
- `DrsReplSchemaTestCase` extends `drs_base.DrsBaseTestCase`.
- `_schema_new_class()` and `_schema_new_attr()` create schema objects with randomized OIDs and call `_ldap_schemaUpdateNow()`.
- `_exop_req8()` builds a level-8 `DsGetNCChanges` request for targeted replication-object checks.
- `_check_object()` confirms an object exists on both DCs, treating `ERR_NO_SUCH_OBJECT` on DC2 as a test failure.

## Control Flow
`setUp()` disables automatic replication on both DCs, forces a clean bidirectional sync, and initializes a shared name prefix. Test cases create schema elements on DC1, update schema now, explicitly replicate the relevant NC to DC2, and verify expected objects. Specialized flows add custom attributes to classes, instantiate custom classes on domain OUs, test a link attribute's returned linked-attribute ATTID against `msDS-IntId`, create binary DN forward/back links, delete linked targets, and rename schema objects.

## State And Persistence Behavior
The module intentionally persists schema changes into the test domain for the lifetime of the environment. It avoids collisions with a timestamp prefix and random OID suffixes but does not remove schema objects, which is typical for AD schema tests because schema deletions are constrained. It temporarily disables automatic replication and restores it in `tearDown()`. Domain OU instances created for domain-NC tests are explicitly deleted where practical.

## Dependencies And Integration Points
It depends on `ldb`, DRSUAPI Python bindings, `misc.GUID`, `samba.dsdb` constants, `drs_DsBind`, and base helpers for replication and schema update. Integration points include the LDAP schema update path, DRS schema NC replication, DRS linked attribute encoding, and schema cache lookup by `attributeID_id` versus `msDS-IntId`.

## Risks
Schema tests are high impact because schema changes are effectively permanent. Random OIDs and names reduce collisions but can still fail if schema constraints or functional level differ. The link attribute test branches on `domainFunctionality` and assumes `msDS-IntId` exists only above Windows 2000 functionality. Replication ordering between schema NC and domain NC is critical for tests that instantiate newly defined classes.

## Test Signals
Signals are existence of new schema objects on both DCs, custom attributes available on newly created classes/OUs, linked attributes not returned with `msDS-IntId` in the schema NC object-replication path, binary DN links surviving replication and target deletion, and renamed classSchema objects visible on DC2 after forced schema replication.
