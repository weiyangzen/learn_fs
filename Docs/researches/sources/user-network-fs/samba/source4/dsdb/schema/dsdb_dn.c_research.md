# sources/user-network-fs/samba/source4/dsdb/schema/dsdb_dn.c

## Purpose
`dsdb_dn.c` converts linked-attribute DSDB DNs between Samba's internal `struct dsdb_dn` representation and the DRS binary blob representation used for replicated linked attributes.

## Important APIs, Types, and Functions
The two exported functions are `dsdb_dn_la_to_blob` and `dsdb_dn_la_from_blob`. Both use `struct dsdb_syntax_ctx`, schema attribute syntax handlers, `drsuapi_DsReplicaAttribute`, `drsuapi_DsAttributeValue`, `ldb_message_element`, and `DATA_BLOB`.

## Control Flow and Behavior
`dsdb_dn_la_to_blob` initializes a default syntax context, linearizes the DSDB DN with extended components, wraps it as a one-value LDB element named after the schema attribute, and calls the attribute syntax `ldb_to_drsuapi` converter. It requires exactly one generated DRS value and returns that blob. `dsdb_dn_la_from_blob` builds a one-value DRS attribute around the input blob, calls `drsuapi_to_ldb`, requires exactly one LDB value, and parses it back through `dsdb_dn_parse` using the syntax LDAP OID.

## State and Persistence Behavior
The functions do not persist state directly. They define the conversion boundary for linked-attribute values that are stored or replicated elsewhere. Returned blobs and DNs are talloc-owned by the supplied memory context.

## Dependencies and Integration Points
The file depends on syntax conversion implementations from the schema layer, DSDB DN parsing/linearization, LDB module types, NDR/DRSUAPI types, and SAMDB schema metadata. It integrates with linked-attribute replication and metadata handling.

## Risks and Edge Cases
Correctness depends on the supplied schema attribute matching the linked DN syntax. Converter output counts other than one are treated as internal errors. `dsdb_dn_get_extended_linearized` must return a valid string for blob conversion; parse failure on the way back becomes a generic internal error. Memory ownership of `drs.value_ctr.values[0].blob` follows converter allocation and must remain valid under `mem_ctx`.

## Test Signals
Round-trip tests should cover normal DN, binary DN, string DN, deleted/extended DN components, malformed blobs, converter failures, zero/multiple converted values, and schema attributes with incompatible syntax.
