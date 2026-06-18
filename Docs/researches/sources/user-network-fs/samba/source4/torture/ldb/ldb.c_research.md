# sources/user-network-fs/samba/source4/torture/ldb/ldb.c

## Purpose

`ldb.c` is a local smbtorture suite for Samba-specific LDB behavior. It tests Samba LDIF syntax handlers, extended DN syntax, DN comparison/validation, binary pack/unpack formats, corrupt unpack handling, LDIF round trips, attribute filtering, and a pack/unpack performance smoke test.

## Important APIs, Types, and Functions

- Static fixtures define SID/GUID/prefixMap strings and binary/LDIF representations of a real directory record.
- `torture_ldb_attrs()` validates `objectSid`, `objectGUID`, and `prefixMap` LDIF read/write/compare handlers.
- `torture_ldb_dn_attrs()` validates extended DN syntax handlers for SID and GUID in clear and hex forms.
- `torture_ldb_dn_extended()` validates parsing, serialization, component removal, and setting of extended GUID/SID components.
- `torture_ldb_dn()` validates normal DN construction/comparison, special DN comparisons, and invalid control characters.
- `torture_ldb_dn_invalid_extended()` validates malformed extended DN rejection.
- `helper_ldb_message_compare()` compares unpacked/parsed messages while skipping known SDDL round-trip differences.
- `torture_ldb_unpack()`, `torture_ldb_unpack_flags()`, `torture_ldb_parse_ldif()`, and `torture_ldb_unpack_and_filter()` validate binary record formats against LDIF.
- `torture_ldb_unpack_data_corrupt()` mutates selected bytes and checks expected unpack success/failure.
- `torture_ldb_pack_data_v2()` and `torture_ldb_pack_data_v2_special()` assert exact v2 packing bytes.
- `torture_ldb_pack_format_perf()` times repeated pack/unpack operations on a large member list.
- `torture_ldb()` registers the local `ldb` suite.

## Control Flow

Most tests initialize a local Samba LDB context with Samba handlers and UTF8 comparison functions, then exercise one API family with fixed fixtures. The binary-format tests use two known packed records, unpack them into `ldb_message`, serialize to LDIF, parse LDIF back, and compare memory forms. The corrupt-data test walks byte ranges classified as corruptible or tolerated, flips bytes, and checks `ldb_unpack_data()` return codes. Suite registration adds simple tests and data-driven cases for both v1 and v2 binary fixtures.

## State and Persistence Behavior

The suite is local and in-memory. It does not connect to LDAP or persist database files. It allocates temporary LDB contexts/messages and frees them through talloc lifetimes. The performance test constructs a large transient LDIF with 10,000 `member` values.

## Dependencies and Integration Points

It depends on LDB core, Samba LDB wrappers, Samba LDIF handlers, DSDB/SAMDB initialization helpers, security descriptor LDIF formatting, UTF8 casefold functions, and the local torture suite registration path. It exercises behavior used by SAMDB storage and replication code.

## Risks and Edge Cases

Exact byte-layout tests are intentionally brittle across LDB packing format changes. `nTSecurityDescriptor` is skipped in deep compare due to known SDDL type-bit differences. DN validation around newlines is currently warning-only for one case. PrefixMap, SID, GUID, and extended DN syntax changes can break many Samba database consumers.

## Test Signals

Signals include successful syntax round trips, rejection of malformed extended DNs, exact packed bytes for v2 records, expected corrupt-byte return codes, LDIF equality for fixture unpacking, reduced LDIF equality after filtering, and successful registration of all v1/v2 data-driven cases.
