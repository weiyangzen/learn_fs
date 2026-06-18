# sources/user-network-fs/samba/source4/torture/drs/rpc/msds_intid.c

## Purpose
`msds_intid.c` is a C DRS torture suite validating ATTID selection rules for attributes with `msDS-IntId`. It proves that schema NC replication uses prefix-map `attributeID_id` ATTIDs, while non-schema NC replication uses `msDS-IntId` when present.

## Important APIs, Types, And Functions
- `struct DsIntIdTestCtx` holds LDAP URL, NC DNs, credentials, DRS bind info, and LDB context.
- `PROVISION_LDIF_FMT` creates a custom normal attribute, linked attribute, updates the User class, and creates a user carrying both attributes.
- `_test_DsaBind()` binds DRS with required `GETCHGREQ_V8` and `GETCHGREPLY_V6` extensions plus baseline extension flags and saves the auth session key.
- `_test_provision()` applies generated LDIF and `schemaUpdateNow` operations over LDAP.
- `_test_GetNCChanges()` fetches a complete NC, accumulating chunks and linked attributes into a single level-6 counter.
- `test_dsintid_schema()` and `_test_dsintid()` assert ATTID rules for schema and non-schema NCs respectively.

## Control Flow
Fixture setup creates context, DRS-binds with required extensions, LDAP-binds, and provisions randomized schema/test data. `_test_GetNCChanges()` sends a level-8 request with writeable, init, periodic, get-ancestors, and never-synced flags, loops through `more_data`, advances high-watermarks, chains object lists, and appends linked attributes. `test_dsintid_schema()` fetches the schema NC, loads schema from the returned prefix map, and asserts every object and linked attribute ATTID equals `attributeID_id` and not `msDS-IntId`. Domain and configuration tests fetch non-schema NCs and assert attributes with `msDS-IntId` use that value, while attributes without it use `attributeID_id`.

## State And Persistence Behavior
The test provisions schema attributes and a test user into the live directory. Like many schema tests, it does not remove schema objects. It opens a DRS policy handle and unbinds it in teardown. Accumulated replication chunks are held in a temporary talloc context per test.

## Dependencies And Integration Points
This file integrates DRSUAPI RPC, LDB/LDAP schema updates, DSDB schema loading from DRS prefix maps, generated NDR structures, linked attribute replication, and Samba torture registration. It specifically exercises the mapping between DRS ATTIDs, `attributeID_id`, and `msDS-IntId` across naming contexts.

## Risks
The test permanently extends schema with randomized IDs, so repeated runs grow the schema. It assumes server support for required DRS extensions and correct schema update behavior before replication fetch. The linked attribute lookup uses `dsdb_attribute_by_attributeID_id()` even when validating `msDS-IntId` cases, making schema map correctness critical. Chunk accumulation manually chains lists and reallocates linked attributes, so memory ownership must remain under the test context.

## Test Signals
Signals include successful DRS bind with required extensions, successful LDIF provisioning, complete level-6 `DsGetNCChanges` fetches, schema NC ATTIDs equal to `attributeID_id` and not `msDS-IntId`, domain/configuration NC ATTIDs equal to `msDS-IntId` when present, fallback to `attributeID_id` otherwise, and the same checks for linked attributes.
