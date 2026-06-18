# sources/user-network-fs/samba/source4/dsdb/common/dsdb_dn.c

## Purpose
`dsdb_dn.c` implements Samba DSDB DN wrapper handling for normal DNs, DN+Binary, DN+String, and DRS object identifiers. It parses and formats prefixed DN syntaxes, canonicalizes/comparisons for LDB schema handlers, and safely converts replication object identifiers into normalized database DNs.

## Important APIs, Types, and Functions
- `dsdb_dn_oid_to_format()` maps syntax OIDs to `DSDB_NORMAL_DN`, `DSDB_BINARY_DN`, `DSDB_STRING_DN`, or invalid.
- `dsdb_dn_construct()` and `dsdb_dn_construct_internal()` assemble `struct dsdb_dn` with a base DN, extra prefix blob, format, and OID.
- `dsdb_dn_parse_trusted()` parses raw LDB values for normal, `B:<hexlen>:<hex>:<dn>`, and `S:<len>:<string>:<dn>` forms.
- `dsdb_dn_parse()` adds `ldb_dn_validate()` on top of trusted parsing.
- `dsdb_dn_get_linearized()`, `dsdb_dn_get_casefold()`, and `dsdb_dn_get_extended_linearized()` format the wrapper.
- `dsdb_dn_binary_canonicalise/comparison()` and string equivalents support LDB syntax comparisons.
- `drs_ObjectIdentifier_to_debug_string()` and `drs_ObjectIdentifier_to_dn_and_nc_root()` handle DRS object identifiers, prioritizing GUID, then SID, then string DN.

## Control Flow
Parsing starts from the syntax OID. Normal DNs are parsed directly and must have no extra part. Binary and string DNs require `B:` or `S:` prefixes, reject embedded NUL by comparing `strlen()` to blob length, parse the declared prefix length, require separator placement, decode hex bytes for binary prefixes, preserve string prefix bytes for string prefixes, parse the trailing DN, then construct the wrapper. Public parsing validates the resulting DN.

Formatting delegates to the underlying LDB DN for the postfix and prepends the appropriate `B:` or `S:` prefix. Canonicalization parses then returns the casefolded representation, making DN comparisons case-insensitive while keeping binary hex uppercase and string prefixes case-sensitive.

DRS object identifier conversion refuses ambiguous/unsafe inputs by honoring GUID/SID priority, validating string DNs, rejecting empty/special/extended DNs, and finally normalizing against the DB while finding the naming-context root.

## State and Persistence
No persistent state is changed. The file creates transient `dsdb_dn`, `ldb_dn`, prefix blobs, debug strings, and normalized DNs. Its comparison/canonicalization output can affect indexed LDB matching and schema behavior.

## Dependencies and Integration Points
Dependencies include SAMDB, LDB module APIs, NDR utilities, domain SID utilities, SMB numeric parsing, GUID/SID formatting, and `dsdb_normalise_dn_and_find_nc_root()`. It is exercised by LDB Samba syntax handlers and DRS replication code.

## Risks and Edge Cases
- DN+Binary length is measured in hex characters and must be even; malformed length/separator combinations are rejected.
- `dsdb_dn_parse_trusted()` skips final `ldb_dn_validate()` by design; callers must use it only for trusted values.
- String prefix bytes are not casefolded, while the DN postfix is.
- DRS string DNs are user-controlled and deliberately avoid logging raw unparsed values in some failure paths.

## Test Signals
`source4/dsdb/common/tests/dsdb_dn.c` directly covers valid construction/parsing, canonicalization/comparison behavior, invalid binary/string prefixes, extended DN rejection for binary syntax, newline/NUL invalid cases, and casefold expectations.
