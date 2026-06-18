# sources/user-network-fs/samba/source4/dsdb/schema/schema_syntax.c

## Purpose

`schema_syntax.c` defines Samba's DSDB schema syntax map and the conversion/validation routines that translate attribute values between local LDB representation and DRSUAPI replication wire blobs. It is the central compatibility layer for Active Directory syntaxes: booleans, integers, large integers, UTC/generalized time, octet strings, OID references, Unicode strings, DN values, DN-binary/DN-string values, OR-Name, presentation addresses, security descriptors, and selected unsupported placeholder syntaxes.

## Important APIs, Types, And Functions

Public APIs include `dsdb_syntax_ctx_init()`, `dsdb_attribute_get_attid()`, `find_syntax_map_by_ad_oid()`, `find_syntax_map_by_ad_syntax()`, `find_syntax_map_by_standard_oid()`, `dsdb_syntax_for_attribute()`, `dsdb_attribute_drsuapi_remote_to_local()`, and `dsdb_attribute_drsuapi_to_ldb()`.

The key data structure is the static `dsdb_syntaxes[]` table. Each `struct dsdb_syntax` row binds an AD syntax tuple (`ldap_oid`, `oMSyntax`, `oMObjectClass`, `attributeSyntax_oid`) to handler callbacks: `drsuapi_to_ldb`, `ldb_to_drsuapi`, and `validate_ldb`. Several rows also define LDB matching rules, comments, `ldb_syntax`, `userParameters`, and `auto_normalise` behavior.

Major internal handler families are `dsdb_syntax_BOOL_*`, `INT32_*`, `INT64_*`, `NTTIME_UTC_*`, `NTTIME_*`, `DATA_BLOB_*`, `OID_*`, `UNICODE_*`, `DN_*`, `DN_BINARY_*`, `DN_STRING_*`, and `PRESENTATION_ADDRESS_*`. `dsdb_syntax_attid_from_remote_attid()` maps remote ATTIDs through a remote prefix map to the local prefix map. `dsdb_syntax_DN_validate_one_val()` is shared validation for DN-like syntaxes.

## Control Flow

Callers normally create a `struct dsdb_syntax_ctx` with `dsdb_syntax_ctx_init()`, optionally set `pfm_remote` for replication from another DC, locate a `struct dsdb_attribute`, then invoke the syntax callback in `attr->syntax`. `dsdb_attribute_drsuapi_to_ldb()` packages that common inbound replication path: initialize context, map the incoming remote ATTID to a local schema attribute, and dispatch to `sa->syntax->drsuapi_to_ldb()`.

Each conversion family follows the same pattern. DRS-to-LDB handlers allocate an `ldb_message_element`, copy the attribute display name, allocate output `ldb_val` slots, validate each incoming blob pointer and size, decode little-endian or NDR data, and write local values. LDB-to-DRSUAPI handlers reject `DRSUAPI_ATTID_INVALID`, set `out->attid` with `dsdb_attribute_get_attid()`, allocate `drsuapi_DsAttributeValue` and backing blobs, encode each LDB value, and attach the blob pointer. Validation handlers check invalid schema attributes, empty values where prohibited, numeric parsing, range bounds, string conversion, DN structure, or round-trip convertibility.

OID conversion is context-sensitive. Some attributes represent class references, some attribute references, and some raw numeric OIDs. `dsdb_syntax_OID_drsuapi_to_ldb()` switches on known ATTIDs and falls back to automatic class/attribute/OID handling. When `schema->relax_OID_conversions` is set during schema acquisition, conversion failures can fall back to raw OID decoding so an incoming schema can be loaded before all referenced definitions are known.

DN conversion uses DRSUAPI object identifier NDR structures. The code preserves GUID and SID extended DN components, rejects RootDSE links, filters extended components so only GUID and SID are accepted, and distinguishes normal DN, binary DN, and string DN formats through `dsdb_dn_parse()` and `dsdb_dn_construct()`.

## State And Persistence Behavior

The file does not persist data directly. Its state is per-call allocation under caller-provided talloc contexts and schema-derived lookup state. The important durable effect is the format of values written into LDB or sent over replication: integers and times are textual in LDB and fixed-width little-endian blobs in DRSUAPI; Unicode strings are converted between Unix charset and UTF-16; DNs preserve extended GUID/SID components; OID references may be stored as LDAP display names or numeric OID strings depending on attribute semantics.

`dsdb_attribute_get_attid()` controls whether an outbound replicated attribute uses `attributeID_id` or `msDS-IntId`, depending on schema NC replication and the presence of `msDS-IntId`.

## Dependencies And Integration Points

This file depends on generated DRSUAPI/NDR structures, LDB value and DN APIs, Samba charset conversion, prefix map helpers, schema lookup helpers, ASN.1 BER OID helpers, NTTIME conversion utilities, GUID/SID extended DN helpers, and talloc memory ownership. It is used by replication encode/decode paths, schema loading, attribute validation, and syntax selection during schema object construction.

## Risks And Edge Cases

Handler behavior is wire-format sensitive. Blob size checks must remain exact for fixed-width values, and time conversion special-cases the zero timestamp as `16010101000000.0Z`. OID handlers depend on complete and correct prefix maps; remote-to-local mapping failures intentionally return schema errors. DN validation has a subtle memory/error-handling risk: after `ldb_dn_copy()`, the code checks `dn == NULL` rather than the copy pointer, so allocation failure of `dn2` could surface later as a generic syntax failure path. Some syntaxes deliberately use `FOOBAR` placeholders or generic blob behavior for rarely used AD syntaxes, which is a compatibility boundary. Range validation for time casts to `int32_t`, so attributes with wide time ranges need care.

## Test Signals

The companion torture tests in `source4/dsdb/schema/tests/schema_syntax.c` verify representative round trips for DN, DN-BINARY, OR-Name, INT32, INT64, NTTIME, BOOL, and Unicode. Additional high-value tests would cover invalid blobs, empty values, range bounds, remote prefix map conversion, relaxed OID conversion during schema replication, DN values with unsupported extended components, and `msDS-IntId` outbound ATTID selection outside the schema NC.
